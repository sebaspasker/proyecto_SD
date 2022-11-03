def dict_sockets():
    return {
        "Register": "1,{alias},{password}",
        "Edit": "2,{alias},{password}",
        "Login": "3,{alias},{password}",
        "Correct": "4,1,Login_correcto",
        "Incorrect": "4,0,Login_incorrecto",
    }
