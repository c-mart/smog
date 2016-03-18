from smog import app

# TODO disable allow other hosts on LAN to connect to debug server
if __name__ == '__main__':
    # This is dangerous to leave running on untrusted networks, remove the host argument to only allow connections from localhost
    app.run(debug=True, host='0.0.0.0')
