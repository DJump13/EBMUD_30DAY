import unittest

import pandas as pd

import data_validation as validation


class DataValidationTests(unittest.TestCase):
    def test_reservoir_volume_accepts_numeric_values(self):
        df = pd.DataFrame(
            {
                "Date": ["2024-01-01"],
                "Year": [2024],
                "Month": [1],
                "Reservoir Volume": [204556],
            }
        )

        cleaned = validation.clean_dataframe(df)
        validation.validate_types(cleaned)

        self.assertEqual(cleaned.loc[0, "Reservoir Volume"], 204556)

    def test_reservoir_volume_accepts_string_values_with_commas(self):
        df = pd.DataFrame(
            {
                "Date": ["2024-01-01"],
                "Year": [2024],
                "Month": [1],
                "Reservoir Volume": ['"204,556"'],
            }
        )

        cleaned = validation.clean_dataframe(df)
        validation.validate_types(cleaned)

        self.assertEqual(cleaned.loc[0, "Reservoir Volume"], 204556)

    def test_fourth_column_can_have_any_reservoir_volume_name(self):
        df = pd.DataFrame(
            {
                "Date": ["2024-01-01"],
                "Year": [2024],
                "Month": [1],
                "Some Reservoir": ['"204,556"'],
            }
        )

        validation.validate_columns(df)
        cleaned = validation.clean_dataframe(df)
        validation.validate_types(cleaned)

        self.assertIn("Reservoir Volume", cleaned.columns)
        self.assertEqual(cleaned.loc[0, "Reservoir Volume"], 204556)


if __name__ == "__main__":
    unittest.main()
