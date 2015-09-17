init -2 python:
    import sys
    sys.path.append(renpy.loader.transfn("scripts"))
    
init -1 python:
    from random import *
    from fse_engine import *
   
init python:
    pass

# The game starts here.
label start:
    $ player = FSECombatant(Person("OldHuntsman", None))
    $ ai = FSECombatant(Person("Slave", None))
    $ sex = FSEngine((player, ai))
    $ sex.start()
    show expression "interface/bg_base.jpg" as bg
    show screen fse_main
    call user_turn
    return
    
label user_turn:    
    $ location_to_call = sex.render_input(ui.interact())
    call expression location_to_call
    return
    
label resolution_phase:
    $ location_to_call = sex.resolution()
    call expression location_to_call
    return

label you_win:
    hide screen fse_main
    menu:
        "You Win!":
            $ pass
    return
    
label game_over:
    hide screen fse_main    
    menu:
        "Game Over":
            $ pass
    return
