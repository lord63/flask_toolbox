import datetime

from flask_toolbox.crawler.pypi import PyPIMeta


def test_pypi_meta_properties():
    meta = PyPIMeta({
        "info": {
            "version": "1.0.0",
            "classifiers": [
                "Programming Language :: Python :: 2.7",
                "Programming Language :: Python :: 3.8",
                "License :: OSI Approved :: MIT License",
            ],
        },
        "urls": [{"upload_time": "2021-02-03T04:05:06"}],
        "releases": {
            "0.1.0": [{"downloads": 3, "upload_time": "2020-01-01T00:00:00"}],
            "0.2.0": [],
            "1.0.0": [
                {"upload_time": "2021-02-03T04:05:06"},
                {"upload_time": "2021-02-03T04:05:07"},
            ],
        },
    }, {
        "data": {
            "last_month": 1200,
        }
    })

    assert meta.download_num == 1200
    assert meta.release_num == 3
    assert meta.current_version == "1.0.0"
    assert meta.released_date == datetime.datetime(2021, 2, 3, 4, 5, 6)
    assert meta.first_release == datetime.datetime(2020, 1, 1, 0, 0, 0)
    assert meta.python_version == "2.7 3.8"
