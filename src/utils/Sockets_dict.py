def dict_sockets():
    return {
        "Register": "1,{alias},{password}",
        "Edit": "2,{alias},{password}",
        "Login": "3,{alias},{password}",
        "Correct": "4,1,Login_correcto",
        "Incorrect": "4,0,Login_incorrecto",
        "Start_Game": "5,Start_Game,{connected}",  # Starts game
        "Start": "5,Start,{connected}",  # Waits until game creates
        "Start_Waiting": "5,Waiting,{connected}",
        "Move": "6,{key},{position},{move_id},{alias}",  # Player Move
        "Player": "7,{alias},{level},{hot},{cold},{dead}",  # Player infomation
        "NPC": "8,{position},{alias},{level},{key},{dead}",  # NPC information
        "Weather": "9,{city_1},{t_1},{city_2},{t_2},{city_3},{t_3},{city_4},{t_4}",
    }


def dict_send_error():
    return {
        "Format_error": "-1,Format connection error, retry connection.",
    }
