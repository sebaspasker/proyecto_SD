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
        "Player": "7,{x},{y},{alias},{level},{hot},{cold},{dead}",  # Player infomation
    }
