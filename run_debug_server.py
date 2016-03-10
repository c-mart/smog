from smog import app

# TODO disable allow other hosts on LAN to connect to debug server
if __name__ == '__main__':
    app.run(debug=True)
    # Run this instead to allow connections from other hosts on LAN (dangerous on untrusted networks)
    # app.run(debug=True, host='0.0.0.0')
