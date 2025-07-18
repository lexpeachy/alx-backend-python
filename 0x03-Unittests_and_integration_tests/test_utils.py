#!/usr/bin/env python3
import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch, Mock


class TestAccessNestedMap(unittest.TestCase):

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        result = access_nested_map(nested_map, path)
        self.assertEqual(result, expected)

   def test_access_nested_map_exception(self):
    # Test case 1
    with self.assertRaises(KeyError) as cm:
        access_nested_map({}, ("a",))
    self.assertEqual(str(cm.exception), "'a'")

    # Test case 2
    with self.assertRaises(KeyError) as cm:
        access_nested_map({"a": 1}, ("a", "b"))
    self.assertEqual(str(cm.exception), "'b'")


class TestGetJson(unittest.TestCase):

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch("utils.requests.get")
    def test_get_json(self, test_url, test_payload, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        result = get_json(test_url)

        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):

    def test_memoize(self):
        class TestClass:

            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(TestClass, 'a_method', return_value=42) as mock_method:
            test_instance = TestClass()

            # Call a_property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Check results
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # Check that a_method was called only once
            mock_method.assert_called_once()
