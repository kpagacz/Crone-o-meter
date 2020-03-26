import os.path
import pathlib

GEAR_TYPE = {
    "green-armor" : "/green-armor",
    "blue-bound-acc" : "/blue-bound-acc",
    "gold-blue-acc" : "/gold-blue-acc",
    "green-acc" : "/green-acc",
    "green-weapon" : "/green-weapon",
    "life-acc" : "/life-acc",
    "life-clothes" : "/life-clothes",
    "silver-clothes" : "/silver-clothes",
    "white-blue-yellow-armor" : "/white-blue-yellow-armor",
    "white-blue-yellow-weapon-life-tool" : "/white-blue-yellow-weapon-life-tool"
}

ENHANCEMENT_LEVEL = {
    "1" : 1,
    "2" : 2,
    "3" : 3,
    "4" : 4,
    "5" : 5,
    "6" : 6,
    "7" : 7,
    "8" : 8,
    "9" : 9,
    "10" : 10,
    "11" : 11,
    "12" : 12,
    "13" : 13,
    "14" : 14,
    "15" : 15,
    "PRI" : "PRI",
    "DUO" : "DUO",
    "TRI" : "TRI",
    "TET" : "TET",
    "PEN" : "PEN",
}

ENHANCE_TABLES_PATH = pathlib.Path(pathlib.Path(__file__).parent.parent.parent, "data", "enhance-tables.h5")

BLACK_STONE_ARMOR_PRICE = 2.00e5
BLACK_STONE_WEAPON_PRICE = 2.00e5
CONCENT_ARMOR_PRICE = 2e6
CONCENT_WEAPON_PRICE = 2e6
BLACK_GEM_PRICE = 1.4e6
CONCENT_BLACK_GEM_PRICE = 1.4e7

REBLATH_FAILSTACK_COSTS_TABLE_KEY = "reblathfscosts"
