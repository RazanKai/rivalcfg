import pytest

from rivalcfg import mouse
from rivalcfg import usbhid
from rivalcfg import mouse_settings

FAKE_PROFILE = {
    "name": "Fake Mouse",
    "vendor_id": 0x1038,
    "product_id": 0xBAAD,
    "endpoint": 2,
    "settings": {
        "setting1": {
            "label": "Setting 1",
            "description": "A setting with no value",
            "cli": ["-1", "--setting1"],
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0xAA, 0xBB],
            "value_type": None,
        },
        "setting2": {
            "label": "Setting 2",
            "description": "A setting with a simple choice value",
            "cli": ["-2", "--setting2"],
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0xCC],
            "value_type": "choice",
            "choices": {
                "foo": 0x01,
                "bar": 0x02,
            },
            "default": "bar",
        },
        "setting3": {
            "label": "Setting 3",
            "description": "A setting that uses HID feature report",
            "cli": ["-3", "--setting3"],
            "report_type": usbhid.HID_REPORT_TYPE_FEATURE,
            "command": [0xC0, 0x10, 0x25],
            "value_type": None,
        },
        "setting4": {
            "label": "Setting 4",
            "description": "A setting that use a fixed packet length",
            "cli": ["-4", "--setting4"],
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0x11, 0x22],
            "packet_length": 10,
            "value_type": None,
        },
        "setting5": {
            "label": "Setting 5",
            "description": "A setting with a command suffix",
            "cli": ["-5", "--setting5"],
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0x11, 0x22],
            "command_suffix": [0x33, 0x44],
            "value_type": "choice",
            "choices": {
                42: 0xAA,
            },
            "default": 42,
        },
        "setting6": {
            "label": "Setting 6",
            "description": "A setting with no value",
            "cli": ["-6", "--setting6"],
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0x20, 0x2E],
            "value_type": "none",
        },
        "setting_readback": {
            "label": "Setting with readback",
            "description": "A setting with no value",
            "cli": ["-7", "--setting7"],
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0x20, 0x2F],
            "value_type": "none",
            "readback_length": 42,
        },
        "setting_no_readback": {
            "label": "Setting without readback",
            "description": "A setting with no value",
            "cli": ["-8", "--setting8"],
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0x20, 0x2F],
            "value_type": "none",
            "readback_length": 0,
        },
    },
    "save_command": {
        "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
        "command": [0x5A, 0x0E],
    },
}

FAKE_PROFILE2 = {
    "name": "Fake Mouse 2",
    "vendor_id": 0x1038,
    "product_id": 0xBAD2,
    "endpoint": 2,
    "settings": {},
    "save_command": {
        "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
        "packet_length": 4,
        "command": [0x5A, 0x0E],
    },
}


class TestGetMouse(object):
    def test_get_mouse_returns_mouse_instance_with_desired_profil(self, monkeypatch):
        monkeypatch.setenv("RIVALCFG_DRY", "1")
        rival100 = mouse.get_mouse(vendor_id=0x1038, product_id=0x1702)
        assert rival100.mouse_profile["vendor_id"] == 0x1038
        assert rival100.mouse_profile["product_id"] == 0x1702

    def test_get_mouse_vendor_id_param_optional(self, monkeypatch):
        monkeypatch.setenv("RIVALCFG_DRY", "1")
        rival100 = mouse.get_mouse(product_id=0x1702)
        assert rival100.mouse_profile["vendor_id"] == 0x1038
        assert rival100.mouse_profile["product_id"] == 0x1702

    def test_get_mouse_raise_error_if_no_product_id(self):
        with pytest.raises(ValueError):
            mouse.get_mouse()

    @pytest.mark.skip("Not implemented yet")
    def test_get_mouse_raise_error_if_profile_does_not_exists(self):
        pass  # TODO


FAKE_PROFILE_READABLE = {
    "name": "Fake Readable Mouse",
    "vendor_id": 0x1038,
    "product_id": 0xBEEF,
    "endpoint": 2,
    "settings": {
        "sensitivity": {
            "label": "Sensitivity presets",
            "description": "Set sensitivity presets (DPI)",
            "cli": ["-s", "--sensitivity"],
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0x2D],
            "value_type": "multidpi_range_choice",
            "input_range": [400, 2200, 200],
            "output_choices": {
                400: 0x04,
                800: 0x09,
                1000: 0x0B,
                1800: 0x14,
                2200: 0x19,
            },
            "dpi_length_byte": 1,
            "first_preset": 0,
            "max_preset_count": 5,
            "default": "400, 800, 1000, 1800, 2200",
            "get_command": [0xAD],
            "response_length": 64,
        },
        "sensitivity_no_length": {
            "label": "Sensitivity presets",
            "description": "A readable setting missing its response length",
            "cli": ["--sensitivity-no-length"],
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0x2D],
            "value_type": "multidpi_range_choice",
            "input_range": [400, 2200, 200],
            "output_choices": {400: 0x04},
            "dpi_length_byte": 1,
            "first_preset": 0,
            "max_preset_count": 5,
            "default": "400",
            "get_command": [0xAD],
        },
        "sensitivity_bad_handler": {
            "label": "Sensitivity presets",
            "description": "A readable setting whose handler cannot decode",
            "cli": ["--sensitivity-bad-handler"],
            "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
            "command": [0x2D],
            "value_type": "choice",
            "choices": {1: 0x01},
            "default": 1,
            "get_command": [0xAD],
            "response_length": 64,
        },
    },
    "save_command": {
        "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
        "command": [0x5A, 0x0E],
    },
}


class FakePipeDevice(usbhid.FakeDevice):
    """A fake device that answers reads the way a HID pipe does.

    A reply is queued when the command that asks for it is *written* -- a real
    device has nothing to hand back before it is asked -- and each read hands
    back one pending report and empties the pipe, so a read on a quiet device
    returns nothing.  :class:`rivalcfg.usbhid.FakeDevice` instead answers every
    read with as many zero bytes as asked for, which no real device does and
    which would hide both the draining of stale reports and a missing answer.

    It also refuses ``timeout_ms=0`` on purpose: on hidapi 0.15.0 a zero
    timeout means "no timeout" and blocks forever, so a read that would hang on
    a real device fails here instead of quietly passing the suite.
    """

    #: 5 presets, the third one selected: what the "get" command gets answered.
    SENSITIVITY_ANSWER = [
        0xAD,
        0x05,
        0x02,
        0x04,
        0x09,
        0x0B,
        0x14,
        0x19,
    ] + [0x00] * 56

    def __init__(self, answers=None, pending=None):
        super().__init__()
        #: Replies the device gives, keyed by the command byte it received.
        self.answers = dict(answers or {})
        #: Reports already waiting to be read, oldest first.
        self.pending = [list(report) for report in (pending or [])]
        #: The ``timeout_ms`` of every read, in order.
        self.read_timeouts = []

    def write(self, data):
        super().write(data)
        command = bytes(data)[1] if len(data) > 1 else None
        if command in self.answers:
            self.pending.append(list(self.answers[command]))

    def read(self, max_length, timeout_ms=0):
        self.read_timeouts.append(timeout_ms)
        assert timeout_ms != 0, "a zero timeout blocks forever on hidapi 0.15.0"
        if self.pending:
            return self.pending.pop(0)
        return []


class TestMouseGetter(object):
    @pytest.fixture
    def device(self):
        return FakePipeDevice(answers={0xAD: FakePipeDevice.SENSITIVITY_ANSWER})

    @pytest.fixture
    def silent_device(self):
        return FakePipeDevice()

    @pytest.fixture
    def mouse(self, device):
        return mouse.Mouse(
            device,
            FAKE_PROFILE_READABLE,
            mouse_settings.FakeMouseSettings(0x1038, 0xBEEF, FAKE_PROFILE_READABLE),
        )

    @pytest.fixture
    def silent_mouse(self, silent_device):
        return mouse.Mouse(
            silent_device,
            FAKE_PROFILE_READABLE,
            mouse_settings.FakeMouseSettings(0x1038, 0xBEEF, FAKE_PROFILE_READABLE),
        )

    def test_get_is_available(self, mouse):
        assert hasattr(mouse, "get_sensitivity")

    def test_unknown_setting(self, mouse):
        with pytest.raises(AttributeError):
            mouse.get_nonsense()

    def test_unreadable_setting(self, mouse):
        with pytest.raises(AttributeError):
            mouse.get_setting1()

    def test_missing_response_length(self, mouse):
        with pytest.raises(ValueError):
            mouse.get_sensitivity_no_length()

    def test_handler_that_cannot_decode(self, mouse):
        with pytest.raises(ValueError):
            mouse.get_sensitivity_bad_handler()

    def test_writes_the_get_command(self, mouse, device):
        mouse.get_sensitivity()
        device.bytes.seek(0)
        assert device.bytes.read() == b"\x02\x00\xad"

    def test_decodes_the_answer(self, mouse):
        assert mouse.get_sensitivity() == {
            "dpis": [400, 800, 1000, 1800, 2200],
            "selected_preset": 2,
        }

    def test_drops_reports_left_over_from_before(self, device):
        # A reply that was never read -- an interrupted run, or an answer that
        # arrived after the previous read had given up -- must not be decoded
        # as the current state.  The stale report says preset 5; the answer to
        # our own question, and so the result, must say preset 3.
        device.pending.append([0xAD, 0x05, 0x04, 0x04, 0x09, 0x0B, 0x14, 0x19])
        readable_mouse = mouse.Mouse(
            device,
            FAKE_PROFILE_READABLE,
            mouse_settings.FakeMouseSettings(0x1038, 0xBEEF, FAKE_PROFILE_READABLE),
        )
        assert readable_mouse.get_sensitivity()["selected_preset"] == 2
        assert device.pending == []

    def test_raises_when_the_device_does_not_answer(self, silent_mouse):
        with pytest.raises(IOError):
            silent_mouse.get_sensitivity()

    def test_never_reads_with_a_zero_timeout(self, mouse, device):
        mouse.get_sensitivity()
        assert 0 not in device.read_timeouts

    def test_reading_does_not_change_the_stored_settings(self, mouse):
        # A read reports what the device says; it must not be recorded as if
        # the library had written it.
        before = mouse.mouse_settings.get("sensitivity")
        mouse.get_sensitivity()
        assert mouse.mouse_settings.get("sensitivity") == before


class TestMouse(object):
    @pytest.fixture
    def mouse(self, monkeypatch):
        return mouse.Mouse(
            usbhid.FakeDevice(),
            FAKE_PROFILE,
            mouse_settings.FakeMouseSettings(0x1038, 0xBAAD, FAKE_PROFILE),
        )

    @pytest.fixture
    def mouse2(self, monkeypatch):
        return mouse.Mouse(
            usbhid.FakeDevice(),
            FAKE_PROFILE2,
            mouse_settings.FakeMouseSettings(0x1038, 0xBAD2, FAKE_PROFILE2),
        )

    def test_name(self, mouse):
        assert mouse.name == "Fake Mouse"

    def test_product_id(self, mouse):
        assert mouse.product_id == 0xBAAD

    def test_firmware_version_tuple(self, mouse):
        assert mouse.firmware_version_tuple == (0,)

    def test_firmware_version(self, mouse):
        assert mouse.firmware_version == "0"

    def test_save(self, mouse):
        mouse.save()
        mouse._hid_device.bytes.seek(0)
        assert mouse._hid_device.bytes.read() == b"\x02\x00\x5a\x0e"

    def test_save_fixed_packet_length(self, mouse2):
        mouse2.save()
        mouse2._hid_device.bytes.seek(0)
        data = mouse2._hid_device.bytes.read()
        assert len(data) == 6
        assert data == b"\x02\x00\x5a\x0e\x00\x00"

    def test_reset_settings(self, mouse):
        mouse.reset_settings()
        mouse._hid_device.bytes.seek(0)
        hid_report = mouse._hid_device.bytes.read()
        assert b"\x02\x00\x5a\x0e" not in hid_report  # No save command
        assert b"\x02\x00\xaa\xbb" in hid_report  # setting1
        assert b"\x02\x00\xcc\x02" in hid_report  # setting2
        assert b"\x03\x00\xc0\x10\x25" in hid_report  # setting3

    def test_repr(self, mouse):
        assert str(mouse) == "<Mouse Fake Mouse (1038:baad:02)>"
        assert repr(mouse) == "<Mouse Fake Mouse (1038:baad:02)>"

    @pytest.mark.parametrize(
        "report_type,expected_hid_report",
        [
            (usbhid.HID_REPORT_TYPE_OUTPUT, b"\x02\x00"),
            (usbhid.HID_REPORT_TYPE_FEATURE, b"\x03\x00"),
        ],
    )
    def test__hid_write_with_a_valid_report_type(
        self, mouse, report_type, expected_hid_report
    ):
        mouse._hid_write(report_type=report_type)
        mouse._hid_device.bytes.seek(0)
        assert mouse._hid_device.bytes.read() == expected_hid_report

    def test__hid_write_with_a_wrong_report_type(self, mouse):
        with pytest.raises(ValueError):
            mouse._hid_write(report_type=0x42)

    def test__hid_write_with_data(self, mouse):
        mouse._hid_write(
            report_type=usbhid.HID_REPORT_TYPE_OUTPUT,
            report_id=0x42,
            data=[0xDA, 0x7A],
        )
        mouse._hid_device.bytes.seek(0)
        assert mouse._hid_device.bytes.read() == b"\x02\x42\xda\x7a"

    def test__hid_write_with_fixed_packet_length(self, mouse):
        mouse._hid_write(packet_length=4)
        mouse._hid_device.bytes.seek(0)
        data = mouse._hid_device.bytes.read()
        assert len(data) == 6
        assert data == b"\x02\x00\x00\x00\x00\x00"

    # Virtual methods dependent to the loaded profile

    def test_set_setting1_is_available(self, mouse):
        assert hasattr(mouse, "set_setting1")

    def test_set_setting1(self, mouse):
        mouse.set_setting1()
        mouse._hid_device.bytes.seek(0)
        assert mouse._hid_device.bytes.read() == b"\x02\x00\xaa\xbb"

    def test_set_setting2_is_available(self, mouse):
        assert hasattr(mouse, "set_setting2")

    @pytest.mark.parametrize(
        "value,expected_hid_report",
        [
            ("foo", b"\x02\x00\xcc\x01"),
            ("bar", b"\x02\x00\xcc\x02"),
        ],
    )
    def test_setting2(self, mouse, value, expected_hid_report):
        mouse.set_setting2(value)
        mouse._hid_device.bytes.seek(0)
        assert mouse._hid_device.bytes.read() == expected_hid_report

    def test_set_setting3_is_available(self, mouse):
        assert hasattr(mouse, "set_setting3")

    def test_set_setting3(self, mouse):
        mouse.set_setting3()
        mouse._hid_device.bytes.seek(0)
        assert mouse._hid_device.bytes.read() == b"\x03\x00\xc0\x10\x25"

    def test_set_setting4_packet_length(self, mouse):
        mouse.set_setting4()
        mouse._hid_device.bytes.seek(0)
        data = mouse._hid_device.bytes.read()
        assert len(data) == 12
        assert data == b"\x02\x00\x11\x22\x00\x00\x00\x00\x00\x00\x00\x00"

    def test_set_setting5_command_suffix(self, mouse):
        mouse.set_setting5(42)
        mouse._hid_device.bytes.seek(0)
        data = mouse._hid_device.bytes.read()
        assert data == b"\x02\x00\x11\x22\xaa\x33\x44"

    def test_an_unexisting_setting(self, mouse):
        assert not hasattr(mouse, "set_xxx")
        with pytest.raises(AttributeError):
            mouse.set_xxx()

    def test_readback(self, mouse):
        response = mouse.set_setting_readback()
        assert len(response) == 42

    def test_no_readback(self, mouse):
        response = mouse.set_setting_no_readback()
        assert response is None
        response = mouse.set_setting6()
        assert response is None
