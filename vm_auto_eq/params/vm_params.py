VOICEMEETER_PARAMS = {
    # =========================
    # INPUT STRIPS
    # =========================
    "strip": {
        "gain": "Strip[{i}].Gain",
        "mute": "Strip[{i}].Mute",
        "solo": "Strip[{i}].Solo",
        "mono": "Strip[{i}].Mono",
        "mc": "Strip[{i}].MC",              # mono center
        "pan_x": "Strip[{i}].Pan_x",
        "pan_y": "Strip[{i}].Pan_y",
        "color_x": "Strip[{i}].Color_x",
        "color_y": "Strip[{i}].Color_y",

        # routing
        "A1": "Strip[{i}].A1",
        "A2": "Strip[{i}].A2",
        "A3": "Strip[{i}].A3",
        "A4": "Strip[{i}].A4",
        "A5": "Strip[{i}].A5",

        "B1": "Strip[{i}].B1",
        "B2": "Strip[{i}].B2",
        "B3": "Strip[{i}].B3",

        # EQ / dynamics
        "eq_on": "Strip[{i}].EQ.on",
        "comp": "Strip[{i}].Comp",
        "gate": "Strip[{i}].Gate",
        "denoiser": "Strip[{i}].Denoiser",

        # effects
        "reverb": "Strip[{i}].Reverb",
        "delay": "Strip[{i}].Delay",

        # label
        "label": "Strip[{i}].Label",
    },

    # =========================
    # OUTPUT BUSES
    # =========================
    "bus": {
        "gain": "Bus[{i}].Gain",
        "mute": "Bus[{i}].Mute",
        "mono": "Bus[{i}].Mono",

        "eq_on": "Bus[{i}].EQ.on",

        "mode_normal": "Bus[{i}].mode.normal",
        "mode_amix": "Bus[{i}].mode.amix",
        "mode_bmix": "Bus[{i}].mode.bmix",
        "mode_repeat": "Bus[{i}].mode.repeat",
        "mode_composite": "Bus[{i}].mode.composite",

        "label": "Bus[{i}].Label",
    },

    # =========================
    # RECORDER
    # =========================
    "recorder": {
        "arm_strip": "Recorder.ArmStrip[{i}]",
        "arm_bus": "Recorder.ArmBus[{i}]",

        "mode_rec": "Recorder.Mode.Rec",
        "mode_play": "Recorder.Mode.Play",
        "load": "Recorder.Load",
        "play": "Recorder.Play",
        "stop": "Recorder.Stop",
        "pause": "Recorder.Pause",
        "record": "Recorder.Record",
        "ff": "Recorder.FF",
        "rew": "Recorder.Rew",
    },

    # =========================
    # VBAN
    # =========================
    "vban": {
        "enable": "VBAN.Enable",

        "instream_on": "VBAN.InStream[{i}].on",
        "instream_name": "VBAN.InStream[{i}].name",
        "instream_ip": "VBAN.InStream[{i}].ip",
        "instream_port": "VBAN.InStream[{i}].port",

        "outstream_on": "VBAN.OutStream[{i}].on",
        "outstream_name": "VBAN.OutStream[{i}].name",
        "outstream_ip": "VBAN.OutStream[{i}].ip",
        "outstream_port": "VBAN.OutStream[{i}].port",
    },

    # =========================
    # OPTION / GLOBAL
    # =========================
    "option": {
        "buffer_ms": "Option.Buffer.ms",
        "sr": "Option.Sr",
        "delay": "Option.Delay[{i}]",
    },

    # =========================
    # COMMANDS
    # =========================
    "command": {
        "restart": "Command.Restart",
        "shutdown": "Command.Shutdown",
        "show": "Command.Show",
        "lock": "Command.Lock",
        "reset": "Command.Reset",
    },

}

VOICEMEETER_EQ_PARAMS = {    
    "eq": {
        "on": "Strip[{i}].EQ.on",
        "base": "Strip[{i}].EQ.band[{band}]",

        "freq": "Strip[{i}].EQ.band[{band}].freq",
        "gain": "Strip[{i}].EQ.band[{band}].gain",
        "q": "Strip[{i}].EQ.band[{band}].q",
        "type": "Strip[{i}].EQ.band[{band}].type",
    },
    "bus_eq": {
        "preset": "Bus[{i}].EQ",
        "on": "Bus[{i}].EQ.on",
        "base": "Bus[{i}].EQ.channel[{channel}].cell[{band}]",

        "freq": "Bus[{i}].EQ.channel[{channel}].cell[{band}].f",
        "gain": "Bus[{i}].EQ.channel[{channel}].cell[{band}].gain",
        "q": "Bus[{i}].EQ.channel[{channel}].cell[{band}].q",
        "type": "Bus[{i}].EQ.channel[{channel}].cell[{band}].type",
    },
    "eq_type": {
        "BELL":         "0",
        "BAND_PASS":    "1",
        "NOTCH":        "2",
        "LOW_PASS":     "3",
        "HIGH_PASS":    "4",
        "LOW_SHELF":    "5",
        "HIGH_SHELF":   "6",
    },
}

def param(section, key, i=None):
    raw = VOICEMEETER_PARAMS[section][key]

    if "{i}" in raw:
        return raw.format(i=i)

    return raw

def eq_param(section, key, i=None, band = None, channel=None):
    raw = VOICEMEETER_EQ_PARAMS[section][key]

    if "{i}" in raw and "{band}" in raw and "{channel}" in raw:
        return raw.format(i=i, band=band, channel=channel)
    elif "{i}" in raw and "{band}" in raw:
        return raw.format(i=i, band=band)
    elif "{i}" in raw:
        return raw.format(i=i)
    return raw