import pandas as pd

from trade_app.services.external_api import ExternalDataService


class DataProcessorService:
    """Service for processing and enriching transaction data."""

    def __init__(self):
        self.external_data_service = ExternalDataService()

    @staticmethod
    def read_csv_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {e}")

    async def enrich_data(self, df: pd.DataFrame) -> pd.DataFrame:

        # Create new columns for requreied data
        df['legal_name'] = ""
        df['bic'] = None
        df['country'] = ""
        df['transaction_costs'] = 0.0

        for idx, row in df.iterrows():
            lei = row['lei']

            fetched_data = await self.external_data_service.fetch_external_data(lei)
            extracted_info = self.external_data_service.extract_required_data(fetched_data)

            # declare extracted data to the dataframe
            df.at[idx, 'legal_name'] = extracted_info['legal_name']
            df.at[idx, 'bic'] = str(extracted_info['bic'])
            df.at[idx, 'country'] = extracted_info['country']

            # Calculate transaction costs 
            notional = row['notional']
            rate = row['rate']
            country = extracted_info['country']

            if country == "GB":
                transaction_costs = notional * rate - notional
            elif country == "NL":
                transaction_costs = abs(notional * (1 / rate) - notional)
            else:
                transaction_costs = 0.0  # Default for other countries

            df.at[idx, 'transaction_costs'] = transaction_costs

        return df

    @staticmethod
    def save_enriched_data(df: pd.DataFrame, output_path: str) -> None:
        try:
            df.to_csv(output_path, index=False)
        except Exception as e:
            raise ValueError(f"Failed to save enriched data: {e}")


# Declare function to process file in background
async def background_process_data(input_path: str, output_path: str):
    data_processor_service = DataProcessorService()
    try:
        df = data_processor_service.read_csv_data(input_path)
        enriched_df = await data_processor_service.enrich_data(df)
        data_processor_service.save_enriched_data(enriched_df, output_path)

    except Exception as e:
        print(f"Error in background processing: {e}")
