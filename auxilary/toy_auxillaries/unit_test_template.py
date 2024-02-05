import unittest
from unittest.mock import patch, MagicMock
from build.api_loader import merge_data


class TestAPILoader(unittest.TestCase):
    @patch("api_loader.requests.get")
    @patch("api_loader.GraphDatabase.driver")
    def test_merge_data(self, mock_driver, mock_get):
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.__dict__[
            "_content"
        ].decode.return_value = '{"components": [{"content": [{"name": "newsarticle", "value": {"title": "Test Article"}}]}]}'
        mock_get.return_value = mock_response

        # Mock the Neo4j driver and session
        mock_session = MagicMock()
        mock_driver.return_value.session.return_value.__enter__.return_value = (
            mock_session
        )

        # Call the merge_data function
        merge_data(mock_session, 12345, '{"title": "Test Article"}')

        # Assert that the Neo4j query was executed with the correct parameters
        mock_session.execute_write.assert_called_once_with(
            merge_data, id=12345, newsarticle='{"title": "Test Article"}'
        )


if __name__ == "__main__":
    unittest.main()
