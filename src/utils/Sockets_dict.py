def dict_sockets():
    return {
        "Register": "1,{alias},{password}",
        "Edit": "2,{alias},{password}",
        "Login": "3,{alias},{password}",
        "Correct": "4,1,Login_correcto",
        "Incorrect": "4,0,Login_incorrecto",
        "Start": "5,Start,{connected}",
        "Start_Waiting": "5,Waiting,{connected}",
    }
