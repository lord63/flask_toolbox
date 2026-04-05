import importlib.util
import pathlib
import textwrap

from flask_toolbox.extensions import db
from flask_toolbox.models import Category, Package


spec = importlib.util.spec_from_file_location(
    "manage_module",
    pathlib.Path(__file__).resolve().parents[1] / "manage.py",
)
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)


def write_packages_file(path, content):
    path.write_text(textwrap.dedent(content), encoding="utf-8")


def test_init_data_seeds_packages_with_categories(app, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    write_packages_file(tmp_path / "packages.yml", """
        categories:
          Testing:
            description: Testing helpers.
            packages:
              - Flask-Testing
        packages:
          Flask:
            description: Baseline package.
            pypi_url: https://pypi.org/project/Flask/
            documentation_url: https://flask.palletsprojects.com/
            source_code_url: https://github.com/pallets/flask
            bug_tracker_url: https://github.com/pallets/flask/issues
          Flask-Testing:
            description: Testing helpers for Flask.
            pypi_url: https://pypi.org/project/Flask-Testing/
            documentation_url: https://pythonhosted.org/Flask-Testing/
            source_code_url: https://github.com/jarus/flask-testing
            bug_tracker_url: https://github.com/jarus/flask-testing/issues
    """)

    manage.init_data.callback.__wrapped__()

    category = Category.query.filter_by(name="Testing").first()
    package = Package.query.filter_by(name="Flask-Testing").first()

    assert Category.query.count() == 1
    assert Package.query.count() == 2
    assert Package.query.filter_by(name="Flask").first().score == 100.0
    assert category is not None
    assert package.category_id == category.id


def test_sync_data_updates_existing_rows_and_assigns_new_categories(app, monkeypatch, tmp_path):
    old_category = Category(name="Testing", description="Old description.")
    old_package = Package(
        category=old_category,
        name="Flask-Testing",
        description="Old package description.",
        score=0.0,
        pypi_url="https://old.example/pypi",
        documentation_url="https://old.example/docs",
        source_code_url="https://old.example/src",
        bug_tracker_url="https://old.example/bugs",
    )
    db.session.add_all([old_category, old_package])
    db.session.commit()

    monkeypatch.chdir(tmp_path)
    write_packages_file(tmp_path / "packages.yml", """
        categories:
          Forms:
            description: Form helpers.
            packages:
              - Flask-WTF
          Testing:
            description: Updated testing helpers.
            packages:
              - Flask-Testing
        packages:
          Flask-Testing:
            description: Fresh package description.
            pypi_url: https://pypi.org/project/Flask-Testing/
            documentation_url: https://pythonhosted.org/Flask-Testing/
            source_code_url: https://github.com/jarus/flask-testing
            bug_tracker_url: https://github.com/jarus/flask-testing/issues
          Flask-WTF:
            description: Forms integration for Flask.
            pypi_url: https://pypi.org/project/Flask-WTF/
            documentation_url: https://flask-wtf.readthedocs.io/
            source_code_url: https://github.com/wtforms/flask-wtf
            bug_tracker_url: https://github.com/wtforms/flask-wtf/issues
    """)

    manage.sync_data.callback.__wrapped__()

    updated_category = Category.query.filter_by(name="Testing").first()
    updated_package = Package.query.filter_by(name="Flask-Testing").first()
    new_category = Category.query.filter_by(name="Forms").first()
    new_package = Package.query.filter_by(name="Flask-WTF").first()

    assert Category.query.count() == 2
    assert Package.query.count() == 2
    assert updated_category.description == "Updated testing helpers."
    assert updated_package.description == "Fresh package description."
    assert updated_package.category_id == updated_category.id
    assert new_package.category_id == new_category.id
