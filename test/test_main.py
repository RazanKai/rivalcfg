import pytest

from rivalcfg import devices
from rivalcfg import mouse
from rivalcfg import mouse_settings
from rivalcfg.__main__ import main

from test_mouse import FakePipeDevice


class TestMainCLI(object):
    def test_print_help(self):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main(["--help"])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main(["-h"])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

    def test_print_version(self):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main(["--version"])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

    def test_print_list(self):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main(["--list"])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

    def test_no_save(self, monkeypatch):
        monkeypatch.setenv("RIVALCFG_DRY", "1")
        monkeypatch.setenv("RIVALCFG_PROFILE", "1038:1702")
        main(["--reset"])
        main(["-r"])
        # just expecting to have no error here... to boring to monkeypatch
        # the module to check if realy work...

    def test_get_sensitivity(self, monkeypatch, capsys):
        profile = devices.get_profile(vendor_id=0x1038, product_id=0x1854)
        monkeypatch.setattr(
            "rivalcfg.__main__.get_first_mouse",
            lambda: mouse.Mouse(
                FakePipeDevice(answers={0xAD: FakePipeDevice.SENSITIVITY_ANSWER}),
                profile,
                mouse_settings.FakeMouseSettings(0x1038, 0x1854, profile),
            ),
        )

        main(["--get-sensitivity"])

        assert capsys.readouterr().out == (
            "Sensitivity presets: preset 3/5 at 1000 DPI"
            " (400, 800, 1000, 1800, 2200)\n"
        )

    def test_get_sensitivity_on_a_device_that_does_not_answer(
        self, monkeypatch, capsys
    ):
        profile = devices.get_profile(vendor_id=0x1038, product_id=0x1854)
        monkeypatch.setattr(
            "rivalcfg.__main__.get_first_mouse",
            lambda: mouse.Mouse(
                FakePipeDevice(),
                profile,
                mouse_settings.FakeMouseSettings(0x1038, 0x1854, profile),
            ),
        )

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main(["--get-sensitivity"])
        assert pytest_wrapped_e.value.code == 1
        assert capsys.readouterr().out.startswith("E: ")
