import yaml


def test_packages_yml_keeps_catalog_entries_and_only_updates_metadata():
    with open("packages.yml", encoding="utf-8") as packages_file:
        data = yaml.safe_load(packages_file)

    assert "Flask-Social" in data["packages"]
    assert "Flask-Security" in data["packages"]
    assert "Flask-CouchDBKit" in data["packages"]
    assert "Jinja-Assets-Compressor" in data["packages"]
