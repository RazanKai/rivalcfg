import argparse

import pytest

from rivalcfg.handlers import multidpi_range_choice


class TestProcessValue(object):
    @pytest.fixture
    def setting_info(self):
        return {
            "value_type": "multidpi_range_choice",
            "input_range": [100, 1000, 100],
            "output_choices": {
                100: 0x00,
                200: 0x02,
                300: 0x03,
                400: 0x05,
                500: 0x06,
                600: 0x08,
                700: 0x10,
                800: 0x11,
                900: 0x13,
                1000: 0x1A,
            },
            "first_preset": 1,
            "max_preset_count": 5,
            "dpi_length_byte": 1,
            "default": "800, 1600",
        }

    @pytest.fixture
    def setting_info2(self):
        return {
            "value_type": "multidpi_range_choice",
            "input_range": [100, 1000, 100],
            "output_choices": {
                100: 0x00,
                200: 0x02,
                300: 0x03,
                400: 0x05,
                500: 0x06,
                600: 0x08,
                700: 0x10,
                800: 0x11,
                900: 0x13,
                1000: 0x1A,
            },
            "first_preset": 1,
            "max_preset_count": 5,
            "dpi_length_byte": 2,
            "default": "800, 1600",
        }

    @pytest.fixture
    def setting_info3(self):
        return {
            "value_type": "multidpi_range_choice",
            "input_range": [100, 1000, 100],
            "output_choices": {
                100: 0x00,
                200: 0x02,
                300: 0x03,
                400: 0x05,
                500: 0x06,
                600: 0x08,
                700: 0x10,
                800: 0x11,
                900: 0x13,
                1000: 0x1A,
            },
            "first_preset": 0,
            "max_preset_count": 5,
            "dpi_length_byte": 1,
            "default": "800, 1600",
        }

    @pytest.mark.parametrize(
        "input_,expected_output",
        [
            (100, [0x01, 0x01, 0x00]),
            ("100", [0x01, 0x01, 0x00]),
            ([100, 200, 300], [0x03, 0x01, 0x00, 0x02, 0x03]),
            ("100, 200, 300", [0x03, 0x01, 0x00, 0x02, 0x03]),
            ("100,200,300", [0x03, 0x01, 0x00, 0x02, 0x03]),
            ("100,200,300,400,500", [0x05, 0x01, 0x00, 0x02, 0x03, 0x05, 0x06]),
        ],
    )
    def test_values(self, setting_info, input_, expected_output):
        assert (
            multidpi_range_choice.process_value(setting_info, input_) == expected_output
        )

    @pytest.mark.parametrize(
        "input_",
        [
            "100, 200, 300, 400, 500, 600",
            [100, 200, 300, 400, 500, 600],
        ],
    )
    def test_too_many_pressets(self, setting_info, input_):
        with pytest.raises(ValueError):
            multidpi_range_choice.process_value(setting_info, input_)

    def test_too_fiew_pressets(self, setting_info):
        with pytest.raises(ValueError):
            multidpi_range_choice.process_value(setting_info, [])

    @pytest.mark.parametrize(
        "selected",
        [0, 1, 2, 3, 4],
    )
    def test_selected_preset(self, setting_info, selected):
        assert multidpi_range_choice.process_value(
            setting_info,
            "100,200,300,400,500",
            selected_preset=selected,
        ) == [0x05, selected + 1, 0x00, 0x02, 0x03, 0x05, 0x06]

    def test_selected_preset_out_of_range(self, setting_info):
        with pytest.raises(ValueError):
            multidpi_range_choice.process_value(
                setting_info,
                "100,200",
                selected_preset=2,
            )

    def test_dpi_length_byte(self, setting_info2):
        # fmt: off
        assert (
            multidpi_range_choice.process_value(setting_info2, "100,200")
            == [0x02, 0x01, 0x00, 0x00, 0x02, 0x00]
            # . CNT,  SEL,  PRESSET1,   PRESSET2
        )
        # fmt: on

    def test_first_preset(self, setting_info3):
        # fmt: off
        assert (
            multidpi_range_choice.process_value(setting_info3, "100,200")
            == [0x02, 0x00, 0x00, 0x02]
            # . CNT,  SEL,  PST1, PST2
        )
        # fmt: on

    def test_mismatch_input_range_and_output_choices_len(self):
        setting_info = {
            "value_type": "multidpi_range_choice",
            "input_range": [100, 1000, 100],
            "output_choices": {
                100: 0x00,
                200: 0x02,
                300: 0x03,
                400: 0x05,
                500: 0x06,
            },
            "first_preset": 1,
            "max_preset_count": 5,
        }
        with pytest.raises(ValueError):
            multidpi_range_choice.process_value(setting_info, [100])

    def test_mismatch_input_range_and_output_choices_min(self):
        setting_info = {
            "value_type": "multidpi_range_choice",
            "input_range": [100, 500, 100],
            "output_choices": {
                10: 0x00,
                200: 0x02,
                300: 0x03,
                400: 0x05,
                500: 0x06,
            },
            "first_preset": 1,
            "max_preset_count": 5,
        }
        with pytest.raises(ValueError):
            multidpi_range_choice.process_value(setting_info, [100])

    def test_mismatch_input_range_and_output_choices_max(self):
        setting_info = {
            "value_type": "multidpi_range_choice",
            "input_range": [100, 500, 100],
            "output_choices": {
                100: 0x00,
                200: 0x02,
                300: 0x03,
                400: 0x05,
                1000: 0x06,
            },
            "first_preset": 1,
            "max_preset_count": 5,
        }
        with pytest.raises(ValueError):
            multidpi_range_choice.process_value(setting_info, [100])


class TestProcessResponse(object):
    @pytest.fixture
    def setting_info(self):
        return {
            "value_type": "multidpi_range_choice",
            "output_choices": {
                400: 0x04,
                800: 0x09,
                1000: 0x0B,
                1800: 0x14,
                2200: 0x19,
            },
            "first_preset": 0,
            "max_preset_count": 5,
            "dpi_length_byte": 1,
        }

    def test_reads_back_the_presets_and_the_selected_one(self, setting_info):
        # The reply carries the command byte, the count, the selected preset
        # and then one output_choices byte per preset -- the layout
        # process_value sends, echoed back.
        assert multidpi_range_choice.process_response(
            setting_info, [0xAD, 0x05, 0x02, 0x04, 0x09, 0x0B, 0x14, 0x19]
        ) == {
            "dpis": [400, 800, 1000, 1800, 2200],
            "selected_preset": 2,
        }

    def test_ignores_whatever_follows_the_last_preset(self, setting_info):
        # The device does not clear its buffer between answers, so a shorter
        # reply still carries the tail of a longer one.  The announced count
        # is what says where the data ends; anything past it must not be
        # decoded as a preset.
        assert multidpi_range_choice.process_response(
            setting_info,
            [0xAD, 0x02, 0x00, 0x04, 0x09, 0x0B, 0x14, 0x19],
        ) == {
            "dpis": [400, 800],
            "selected_preset": 0,
        }

    def test_first_preset_is_subtracted(self, setting_info):
        setting_info["first_preset"] = 1
        assert (
            multidpi_range_choice.process_response(
                setting_info, [0xAD, 0x02, 0x01, 0x04, 0x09]
            )["selected_preset"]
            == 0
        )

    def test_no_preset(self, setting_info):
        with pytest.raises(ValueError):
            multidpi_range_choice.process_response(
                setting_info, [0xAD, 0x00, 0x00] + [0x00] * 61
            )

    def test_truncated_response(self, setting_info):
        with pytest.raises(ValueError):
            multidpi_range_choice.process_response(
                setting_info, [0xAD, 0x05, 0x02, 0x04]
            )

    def test_too_short_response(self, setting_info):
        with pytest.raises(ValueError):
            multidpi_range_choice.process_response(setting_info, [0xAD, 0x05])

    def test_unknown_dpi_byte(self, setting_info):
        with pytest.raises(ValueError):
            multidpi_range_choice.process_response(
                setting_info, [0xAD, 0x01, 0x00, 0xFF]
            )


class TestFormatResponse(object):
    @pytest.fixture
    def setting_info(self):
        return {"label": "Sensitivity presets"}

    def test_format(self, setting_info):
        assert (
            multidpi_range_choice.format_response(
                setting_info,
                {"dpis": [400, 800, 1000, 1800, 2200], "selected_preset": 2},
            )
            == "Sensitivity presets: preset 3/5 at 1000 DPI (400, 800, 1000, 1800, 2200)"
        )

    def test_single_preset(self, setting_info):
        assert (
            multidpi_range_choice.format_response(
                setting_info, {"dpis": [800], "selected_preset": 0}
            )
            == "Sensitivity presets: preset 1/1 at 800 DPI (800)"
        )

    def test_out_of_range_selected_preset(self, setting_info):
        with pytest.raises(ValueError):
            multidpi_range_choice.format_response(
                setting_info, {"dpis": [400, 800], "selected_preset": 2}
            )

    def test_no_preset(self, setting_info):
        with pytest.raises(ValueError):
            multidpi_range_choice.format_response(
                setting_info, {"dpis": [], "selected_preset": 0}
            )


class TestAddCliOption(object):
    @pytest.fixture
    def cli(self):
        cli = argparse.ArgumentParser()
        multidpi_range_choice.add_cli_option(
            cli,
            "sensitivity42",
            {
                "label": "Sensibility presets",
                "description": "Set sensitivity presets (DPI)",
                "cli": ["-s", "--sensitivity", "--foobar"],
                "command": [0x03, 0x01],
                "value_type": "multidpi_range_choice",
                "input_range": [100, 500, 100],
                "output_choices": {
                    100: 0x00,
                    200: 0x02,
                    300: 0x03,
                    400: 0x05,
                    500: 0x06,
                },
                "first_preset": 1,
                "max_preset_count": 5,
                "default": [100, 200],
            },
        )
        return cli

    def test_cli_options(self, cli):
        assert "-s" in cli.format_help()
        assert "--sensitivity" in cli.format_help()
        assert "--foobar" in cli.format_help()

    def test_cli_metavar(self, cli):
        assert "-s SENSITIVITY42" in cli.format_help()

    @pytest.mark.parametrize(
        "value",
        [
            "200",
            "210",
            "7200, 400",
        ],
    )
    def test_passing_valid_value(self, cli, value):
        params = cli.parse_args(["--sensitivity", value])
        assert params.SENSITIVITY42 == value

    def test_passing_invalid_value(self, cli):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.parse_args(["--sensitivity", "hello"])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 2

    def test_passing_too_much_values(self, cli):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli.parse_args(["--sensitivity", "1,2,3,4,5,6"])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 2
