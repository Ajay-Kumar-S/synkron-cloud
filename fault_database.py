FAULT_TREE = {

    # 1️⃣ BLOWER FAILURE
    "blower_not_working": {

        "initial_question": "Is blower receiving supply voltage at its input terminals?",

        "yes": {
            "question": "Is control signal from PCB present at blower relay output?",
            "yes": {
                "question": "Is blower motor winding continuity normal?",
                "yes": {
                    "result": "Mechanical blockage or bearing jam suspected. Inspect physically before replacement."
                },
                "no": {
                    "result": "Blower motor winding failure confirmed. Replace blower motor."
                }
            },
            "no": {
                "question": "Is relay energizing when blower command is given?",
                "yes": {
                    "result": "Relay contact failure. Replace relay before replacing PCB."
                },
                "no": {
                    "result": "PCB output driver failure suspected. Verify driver transistor before PCB replacement."
                }
            }
        },

        "no": {
            "question": "Is upstream fuse or MCB healthy?",
            "yes": {
                "result": "Wiring discontinuity between supply and blower. Check harness continuity."
            },
            "no": {
                "result": "Fuse blown or MCB tripped. Investigate short circuit before resetting."
            }
        }
    },

    # 2️⃣ COP NOT WORKING
    "cop_not_working": {

        "initial_question": "Is COP display powered (backlight ON)?",

        "yes": {
            "question": "Are buttons responding or sending signal to controller?",
            "yes": {
                "result": "Signal wiring between COP and controller intermittent. Check connector pins."
            },
            "no": {
                "result": "Touch panel or button matrix failure. Replace COP panel after signal verification."
            }
        },

        "no": {
            "question": "Is supply voltage reaching COP board?",
            "yes": {
                "result": "COP internal power regulator failure. Repair or replace COP board."
            },
            "no": {
                "result": "Check traveling cable continuity or loose termination."
            }
        }
    },

    # 3️⃣ DOOR NOT CLOSING
    "door_not_closing": {

        "initial_question": "Is door safety sensor clear and aligned?",

        "yes": {
            "question": "Is door motor receiving command voltage?",
            "yes": {
                "question": "Is motor drawing current?",
                "yes": {
                    "result": "Mechanical obstruction or track misalignment suspected."
                },
                "no": {
                    "result": "Door motor internal winding failure."
                }
            },
            "no": {
                "result": "Door controller output stage failure."
            }
        },

        "no": {
            "result": "Door sensor misalignment or sensor PCB failure."
        }
    },

    # 4️⃣ ELEVATOR NOT MOVING
    "elevator_not_moving": {

        "initial_question": "Is safety chain closed?",

        "yes": {
            "question": "Is drive receiving run command?",
            "yes": {
                "question": "Is motor current detected?",
                "yes": {
                    "result": "Brake not releasing fully or mechanical jam."
                },
                "no": {
                    "result": "Drive output IGBT failure or motor winding open."
                }
            },
            "no": {
                "result": "Controller not issuing run command. Check logic inputs."
            }
        },

        "no": {
            "result": "Open safety circuit. Inspect door lock, emergency stop, overspeed governor switch."
        }
    },

    # 5️⃣ FALSE OVERLOAD
    "overload_false_trigger": {

        "initial_question": "Is load cell reading fluctuating without load?",

        "yes": {
            "result": "Load cell calibration drift or noise interference."
        },

        "no": {
            "result": "Overload PCB signal processing fault."
        }
    },

    # 6️⃣ LEVELING ERROR
    "leveling_error": {

        "initial_question": "Is encoder feedback stable?",

        "yes": {
            "question": "Is brake releasing smoothly?",
            "yes": {
                "result": "Controller leveling parameter tuning required."
            },
            "no": {
                "result": "Brake delay causing overshoot."
            }
        },

        "no": {
            "result": "Encoder misalignment or feedback cable issue."
        }
    },

    # 7️⃣ RANDOM MCB TRIP
    "mcb_tripping_random": {

        "initial_question": "Does MCB trip during motor start?",

        "yes": {
            "result": "Inrush current spike. Check soft starter or VFD ramp settings."
        },

        "no": {
            "result": "Possible insulation breakdown or intermittent short circuit."
        }
    }
}
