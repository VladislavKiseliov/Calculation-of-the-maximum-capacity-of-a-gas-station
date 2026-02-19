from dataclasses import dataclass
from typing import Dict, List, Tuple

import pandas as pd


def summarize_constraints(constraints_df: pd.DataFrame):
    if constraints_df is None or constraints_df.empty:
        raise ValueError("Пустая таблица ограничений для агрегации результата")

    numeric_df = constraints_df.apply(pd.to_numeric, errors="coerce")
    if numeric_df.isna().all().all():
        raise ValueError("Таблица ограничений не содержит числовых данных")

    q_final = numeric_df.min(axis=0, skipna=True)
    limiting_table = numeric_df.idxmin(axis=0, skipna=True)

    def _margin_to_second_min(column: pd.Series):
        values = column.dropna().sort_values()
        if len(values) < 2:
            return float("nan")
        return float(values.iloc[1] - values.iloc[0])

    margin_to_next = numeric_df.apply(_margin_to_second_min, axis=0)
    return q_final, limiting_table, margin_to_next


def _pin_sort_key(pin_col: str) -> float:
    try:
        return float(pin_col.replace("Pin_", "").replace("_", "."))
    except ValueError:
        return float("inf")


def prepare_line_plot_data(df_result: pd.DataFrame) -> Tuple[List[str], List[str], List, Dict]:
    if df_result is None or df_result.empty:
        raise ValueError("Пустая результирующая таблица для построения графика")

    sorted_columns = sorted(df_result.columns, key=_pin_sort_key)
    input_pressure_labels = [c.replace("Pin_", "").replace("_", ".") for c in sorted_columns]
    output_pressure_values = df_result.index.tolist()
    series_by_output = {}
    for output_pressure in output_pressure_values:
        series_by_output[output_pressure] = pd.to_numeric(
            df_result.loc[output_pressure, sorted_columns],
            errors="coerce",
        )
    return sorted_columns, input_pressure_labels, output_pressure_values, series_by_output


def prepare_limiting_map_data(df_limiting: pd.DataFrame):
    if df_limiting is None or df_limiting.empty:
        raise ValueError("Пустая таблица ограничений для построения карты")

    sorted_columns = sorted(df_limiting.columns, key=_pin_sort_key)
    output_pressure_values = df_limiting.index.tolist()
    pin_labels = [c.replace("Pin_", "").replace("_", ".") for c in sorted_columns]

    table_names = sorted(
        {
            str(v)
            for v in df_limiting[sorted_columns].stack().dropna().tolist()
            if str(v).strip()
        }
    )
    if not table_names:
        raise ValueError("Таблица ограничений не содержит значений limiting_table")

    table_to_code = {name: idx for idx, name in enumerate(table_names)}
    code_matrix = (
        df_limiting[sorted_columns]
        .apply(lambda col: col.astype(str).map(table_to_code).fillna(-1).astype(int))
        .to_numpy()
    )
    return pin_labels, output_pressure_values, table_names, code_matrix


def build_final_results_long(
    df_result: pd.DataFrame, df_limiting: pd.DataFrame, df_margin: pd.DataFrame
) -> pd.DataFrame:
    if df_result is None or df_result.empty:
        raise ValueError("Результирующая таблица пуста")

    rows = []
    sorted_columns = sorted(df_result.columns, key=_pin_sort_key)

    for p_out in df_result.index.tolist():
        for pin_col in sorted_columns:
            q_final = pd.to_numeric(pd.Series([df_result.at[p_out, pin_col]]), errors="coerce").iloc[0]
            limiting_table = (
                df_limiting.at[p_out, pin_col]
                if (df_limiting is not None and pin_col in df_limiting.columns and p_out in df_limiting.index)
                else None
            )
            margin_to_next = (
                pd.to_numeric(pd.Series([df_margin.at[p_out, pin_col]]), errors="coerce").iloc[0]
                if (df_margin is not None and pin_col in df_margin.columns and p_out in df_margin.index)
                else float("nan")
            )
            rows.append(
                {
                    "P_out": p_out,
                    "Pin": pin_col.replace("Pin_", "").replace("_", "."),
                    "Q_final": q_final,
                    "limiting_table": limiting_table,
                    "margin_to_next": margin_to_next,
                }
            )

    return pd.DataFrame(rows)


@dataclass
class CalculationRunResult:
    df_result: pd.DataFrame
    df_limiting: pd.DataFrame
    df_margin: pd.DataFrame
    df_final_long: pd.DataFrame


class CalculationApplicationService:
    """Application-layer orchestration for full calculation pipeline."""

    def __init__(self, model, max_performance, logger):
        self.model = model
        self.max_performance = max_performance
        self.logger = logger

    def run_full_calculation(self) -> CalculationRunResult:
        input_pressure = self.model.get_pressure_range("input")
        output_pressure = self.model.get_pressure_range("output")
        tables = self.model.get_table_manager()
        temperature = self.model.get_temperature()
        gas_composition = self.model.load_gas_composition()

        tables_data = {}
        for table_name in tables:
            tables_data[table_name] = self.model.get_table_data(table_name)

        try:
            boiler_data = self.model.get_db_table("Boiler_data")
        except Exception:
            boiler_data = []

        self.logger.debug(f"Данные таблиц для расчета: {tables_data}")

        df_result = pd.DataFrame()
        df_limiting = pd.DataFrame()
        df_margin = pd.DataFrame()

        for p_out in output_pressure:
            df = self.max_performance.calculate(
                input_pressure,
                p_out,
                tables,
                temperature,
                gas_composition,
                tables_data,
                boiler_data=boiler_data,
            )

            self.model.save_intermedia(df, f"Промежуточный результат для P_out={p_out}", index_flag=True)

            q_final, limiting_table, margin_to_next = summarize_constraints(df)

            row_final = pd.DataFrame([q_final], index=[p_out])
            row_limiting = pd.DataFrame([limiting_table], index=[p_out])
            row_margin = pd.DataFrame([margin_to_next], index=[p_out])

            df_result = pd.concat([df_result, row_final])
            df_limiting = pd.concat([df_limiting, row_limiting])
            df_margin = pd.concat([df_margin, row_margin])

        df_final_long = build_final_results_long(df_result, df_limiting, df_margin)

        self.model.save_intermedia(df_result, "Результирующая таблица")
        self.model.save_intermedia(df_limiting, "Результирующая таблица ограничений")
        self.model.save_intermedia(df_margin, "Результирующая таблица запасов")
        self.model.save_intermedia(df_final_long, "Результирующая сводная таблица", index_flag=False)

        return CalculationRunResult(
            df_result=df_result,
            df_limiting=df_limiting,
            df_margin=df_margin,
            df_final_long=df_final_long,
        )
