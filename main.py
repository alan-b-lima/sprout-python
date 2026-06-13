import cmds.ex1.client
import cmds.ex1.server
import cmds.ex4.client
import cmds.ex4.server
from   internal import net
import sys

def main():
    if len(sys.argv) < 3:
        print("usage sprout <exercise> ( client | server ) <ip>:<port>")
        sys.exit(1)

    addr = net.ParseAddr(sys.argv[3])
    if not addr.Ok():
        print(f"invalid addr {addr.Err()}")
        return

    ex, dom = sys.argv[1], sys.argv[2]
    addr = addr.Val()

    match ex, dom:
        case ("ex1", "client"): cmds.ex1.client.Handle(addr)
        case ("ex1", "server"): cmds.ex1.server.Handle(addr)

        case ("ex4", "client"): cmds.ex4.client.Handle(addr)
        case ("ex4", "server"): cmds.ex4.server.Handle(addr)

        case _:
            print("unknown exercise")
            sys.exit(1)

if __name__ == "__main__":
    main()
