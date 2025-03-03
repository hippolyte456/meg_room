

import importlib
import meg_config # TODO change name to meg_room.or expe_room
import meg_config._stim_pc
import meg_config.room as room


from meg_config.room import CONFIG_PATH, USER_CONFIG_PATH

meg_ns  = room.MegRoom(CONFIG_PATH, USER_CONFIG_PATH)