import unittest

from jinja2 import Template

from dags.batchml import corsql, force_prod_sql_template


class TestBatchML(unittest.TestCase):
    def test_corv(self):
        self.assertEqual(
            corsql("SELECT 1", "viewname"),
            "CREATE OR REPLACE VIEW viewname AS SELECT 1;",
        )

    def test_env_jinja(self):
        self.assertRegex(
            Template(force_prod_sql_template).render(
                target_dataset="asdf",
                model_code="qwerty",
                version_code="v1",
            ),
            "EXISTS asdf.qwerty_v1_preds_prod",
        )
