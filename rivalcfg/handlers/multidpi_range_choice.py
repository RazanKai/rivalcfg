"""
The "multidpi_range_choice" type alows to pick values in an input range and
transforms it into values from a fixed output list. If the input values do not
correspond to one of the available output choices, they are rounded to match the
nearest DPI.

This type is used to support devices where we can configure from ``1`` to ``n``
DPI settings in a single command, like the Aerox 3.

For example with an input range like ``[0, 1000, 100]`` and an output range
like ``{0: 0, 100: 1, 200: 2, 300: 4,...}``, you can have the following pair:

* ``0`` -> ``0``
* ``100`` -> ``1``
* ``110`` -> ``1`` (``1100`` rounded to ``100``)
* ``190`` -> ``2`` (``1900`` rounded to ``200``)
* ``200`` -> ``2``
* ``300`` -> ``4``
* ...


Device Profile
--------------

Example of a multidpi_range_choice value type in a device profile:

::

    profile = {

        # ...

        "settings": {

            "sensitivity1": {
                "label": "Sensitivity presets",
                "description": "Set sensitivity presets (DPI)",
                "cli": ["-s", "--sensitivity"],
                "report_type": usbhid.HID_REPORT_TYPE_OUTPUT,
                "command": [0x0B, 0x00],
                "value_type": "multidpi_range_choice",
                "input_range": [100, 18000, 100],
                "output_choices": {
                    100: 0x00,
                    200: 0x02,
                    300: 0x03,
                    400: 0x04,
                    ...
                    18000: 0xD6,
                },
                "dpi_length_byte": 1,    # Little endian
                "first_preset": 1,
                "max_preset_count": 5,
                "default": "800, 1600",
            },

        },

        # ...

    }


CLI
---

Example of CLI option generated with this handler::

   -s SENSITIVITY, --sensitivity SENSITIVITY
                        Set sensitivity preset (DPI) (up to 5 settings, from 200 dpi to 8500
                        dpi, default: '800, 1600')

Example of CLI usage::

    rivalcfg --sensitivity 1600
    rivalcfg --sensitivity "800,1600"
    rivalcfg --sensitivity "200, 400, 800, 1600, 8000"


Reading the value back
----------------------

A device that can be asked what its sensitivity currently is declares how to
ask, and this handler knows how to decode the answer::

    "sensitivity": {
        # ...
        "get_command": [0xAD],
        "response_length": 64,
    },

``get_command`` is the write command with the read bit (``0x80``) set, and
``response_length`` is how many bytes the device answers with.  Declaring
them is all it takes: :class:`rivalcfg.mouse.Mouse` then provides a
``get_sensitivity()`` method (and raises :class:`AttributeError` on devices that
do not declare them, rather than inventing a value), while the CLI grows a
``--get-sensitivity`` option beside ``--sensitivity``::

    $ rivalcfg --get-sensitivity
    Sensitivity presets: preset 3/5 at 1000 DPI (400, 800, 1000, 1800, 2200)

The answer is the device's own state, so it also reports a preset that was
selected with the mouse's DPI button rather than by the host -- a change that is
otherwise invisible to the computer.


Functions
---------
"""

from .range_choice import process_range_choice
from .multidpi_range import cli_multirange_validator
from ..helpers import merge_bytes, uint_to_little_endian_bytearray


def process_value(setting_info, value, selected_preset=None):
    """Called by the :class:`rivalcfg.mouse.Mouse` class when processing a
    "multidpi_range_choice" type setting.

    :param dict setting_info: The information dict of the setting from the
                              device profile.
    :param value: The input value.
    :param int selected_preset: The DPI preset to select (0 is always the
                                first preset).
    :rtype: list[int]
    """
    dpis = []

    if isinstance(value, (int, float)):
        dpis = [int(value)]
    elif isinstance(value, (list, tuple)):
        dpis = [int(dpi) for dpi in value]
    else:
        dpis = [int(dpi) for dpi in value.replace(" ", "").split(",")]

    # Selected preset

    if selected_preset is None:
        selected_preset = setting_info["first_preset"]
    else:
        selected_preset += setting_info["first_preset"]

    # checks

    if len(dpis) == 0:
        raise ValueError("you must provide at least one preset")

    if len(dpis) > setting_info["max_preset_count"]:
        raise ValueError(
            "you provided %i preset but the device accepts a maximum of %i presets"
            % (len(dpis), setting_info["max_preset_count"])
        )

    if "first_preset" not in setting_info:
        raise ValueError(
            "Missing 'first_preset' parameter for 'multidpi_range_choice' handler"
        )

    if (
        not setting_info["first_preset"]
        <= selected_preset
        < len(dpis) + setting_info["first_preset"]
    ):
        raise ValueError("the selected preset is out of range")

    if "dpi_length_byte" not in setting_info:
        raise ValueError(
            "Missing 'dpi_length_byte' parameter for 'multidpi_range_choice' handler"
        )

    dpi_length = setting_info["dpi_length_byte"]

    # DPIs

    output_values = []

    for dpi in dpis:
        output_value = process_range_choice(setting_info, dpi)
        output_value = uint_to_little_endian_bytearray(output_value, dpi_length)
        output_values = merge_bytes(output_values, output_value)

    # Count

    dpi_count = len(dpis)

    #

    return merge_bytes(dpi_count, selected_preset, output_values)


def process_response(setting_info, data):
    """Called by the :class:`rivalcfg.mouse.Mouse` class to decode the device's
    answer to a *read* of a "multidpi_range_choice" type setting.

    The device echoes the command it was asked for and then the setting in
    exactly the layout :func:`process_value` sends it, which is what makes the
    read-back possible at all::

        [0]              the command byte, echoed
        [1]              the number of configured presets
        [2]              the selected preset (``first_preset`` included)
        [3..3+count-1]   one "output_choices" byte per preset

    Anything after the presets is left over from an earlier, longer answer --
    the device does not clear its buffer -- so the reply is *sliced by the
    announced count* rather than read to its end.  Doing otherwise is how a
    five-preset read taken straight after a three-preset one comes back with
    the two presets that no longer exist.

    :param dict setting_info: The information dict of the setting from the
                              device profile.
    :param data: The bytes read back from the device.
    :rtype: dict
    :return: ``{"dpis": [...], "selected_preset": int}``, where
             ``selected_preset`` is zero-based -- the same convention
             :func:`process_value` takes, with ``first_preset`` already
             subtracted.
    """
    if len(data) < 3:
        raise ValueError("the device did not return a sensitivity config")

    preset_count = data[1]
    if preset_count < 1:
        raise ValueError("the device did not return any sensitivity preset")
    if len(data) < 3 + preset_count:
        raise ValueError(
            "truncated sensitivity config: %i preset(s) announced, %i byte(s) read"
            % (preset_count, len(data))
        )

    output_choices = setting_info["output_choices"]
    by_output_value = {value: dpi for dpi, value in output_choices.items()}

    dpis = []
    for output_value in data[3 : 3 + preset_count]:
        if output_value not in by_output_value:
            raise ValueError(
                "unknown DPI value 0x%02X in the sensitivity config" % output_value
            )
        dpis.append(by_output_value[output_value])

    return {
        "dpis": dpis,
        "selected_preset": data[2] - setting_info.get("first_preset", 0),
    }


def format_response(setting_info, value):
    """Render a :func:`process_response` result for the CLI.

    One line, so it can be read by a human and parsed by a script alike: the
    selected preset, its DPI, and the whole preset list (which the caller needs
    to map :attr:`selected_preset` back to a DPI value of its own).

    :param dict setting_info: The information dict of the setting from the
                              device profile.
    :param dict value: A :func:`process_response` result.
    :rtype: str
    """
    dpis = value["dpis"]
    selected = value["selected_preset"]

    if not dpis or not 0 <= selected < len(dpis):
        raise ValueError(
            "the device returned an out of range selected preset (%i/%i)"
            % (selected + 1, len(dpis))
        )

    return "%s: preset %i/%i at %i DPI (%s)" % (
        setting_info["label"],
        selected + 1,
        len(dpis),
        dpis[selected],
        ", ".join(str(dpi) for dpi in dpis),
    )


def add_cli_option(cli_parser, setting_name, setting_info):
    """Add the given "range" type setting to the given CLI arguments parser.

    :param ArgumentParser cli_parser: An :class:`ArgumentParser` instance.
    :param str setting_name: The name of the setting.
    :param dict setting_info: The information dict of the setting from the
                              device profile.
    """
    description = "%s (up to %i settings, from %i dpi to %i dpi, default: '%s')" % (
        setting_info["description"],
        setting_info["max_preset_count"],
        setting_info["input_range"][0],
        setting_info["input_range"][1],
        str(setting_info["default"]),
    )
    cli_parser.add_argument(
        *setting_info["cli"],
        help=description,
        dest=setting_name.upper(),
        metavar=setting_name.upper(),
        action=cli_multirange_validator(setting_info["max_preset_count"]),
    )
