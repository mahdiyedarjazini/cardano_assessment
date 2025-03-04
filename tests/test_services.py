import unittest
from unittest.mock import AsyncMock, MagicMock

import pandas as pd

from trade_app.services.external_api import ExternalDataService
from trade_app.services.transaction_processor import DataProcessorService


class TestExternalDataService(unittest.TestCase):
    def setUp(self):
        self.service = ExternalDataService()
        self.test_lei = "123456789ABCDEFGHIJK"

    def test_extract_required_data(self):
        response_data = {
            "data": [{
                "attributes": {
                    "entity": {
                        "legalName": {"name": "Global Tech Solutions"},
                        "legalAddress": {"country": "US"}
                    },
                    "bic": ["GTECUS33", "GTECUS44"]
                }
            }]
        }

        actual_result = ExternalDataService.extract_required_data(response_data)

        expected_result = {
            "legal_name": "Global Tech Solutions",
            "bic": ["GTECUS33", "GTECUS44"],
            "country": "US"
        }
        self.assertEqual(actual_result, expected_result)


class TestDataProcessorService(unittest.TestCase):
    def setUp(self):
        self.data_processor = DataProcessorService()
        self.sample_data = pd.DataFrame({
            'lei': ['123456', '789012', '345678'],
            'national': [10000.0, 20000.0, 15000.0],
            'rate': [1.1, 0.9, 1.2]
        })

    async def test_enrich_data(self):
        mock_external_service = MagicMock()
        mock_external_service.fetch_external_data = AsyncMock(side_effect=[
            {
                "data": [{
                    "attributes": {
                        "entity": {
                            "legalName": {"name": "Company A"},
                            "legalAddress": {"country": "GB"}
                        },
                        "bic": ["ABCDEF01"]
                    }
                }]
            },
            {
                "data": [{
                    "attributes": {
                        "entity": {
                            "legalName": {"name": "Company B"},
                            "legalAddress": {"country": "NL"}
                        },
                        "bic": ["GHIJKL02"]
                    }
                }]
            },
            {
                "data": [{
                    "attributes": {
                        "entity": {
                            "legalName": {"name": "Company C"},
                            "legalAddress": {"country": "US"}
                        },
                        "bic": ["MNOPQR03"]
                    }
                }]
            }
        ])
        mock_external_service.extract_required_data = MagicMock(side_effect=[
            {
                "legal_name": "Company A",
                "bic": ["ABCDEF01"],
                "country": "GB"
            },
            {
                "legal_name": "Company B",
                "bic": ["GHIJKL02"],
                "country": "NL"
            },
            {
                "legal_name": "Company C",
                "bic": ["MNOPQR03"],
                "country": "US"
            }
        ])

        self.data_processor.external_data_service = mock_external_service


        enriched_df = await self.data_processor.enrich_data(self.sample_data.copy())

        self.assertEqual(enriched_df['legal_name'].tolist(),
                         ["Company A", "Company B", "Company C"])
        self.assertEqual(enriched_df['country'].tolist(),
                         ["GB", "NL", "US"])

        expected_costs = [
            10000.0 * 1.1 - 10000.0,  # GB calculation
            abs(20000.0 * (1 / 0.9) - 20000.0),  # NL calculation
            0.0  # US default
        ]
        self.assertAlmostEqual(enriched_df['transaction_costs'].tolist()[0], expected_costs[0])
        self.assertAlmostEqual(enriched_df['transaction_costs'].tolist()[1], expected_costs[1])
        self.assertAlmostEqual(enriched_df['transaction_costs'].tolist()[2], expected_costs[2])
