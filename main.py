from   internal import net
import sys

def main():
    if len(sys.argv) < 4:
        print("usage sprout <exercise> ( client | server ) <ip>:<port> [ <name> ]")
        sys.exit(1)

    addr = net.ParseAddr(sys.argv[3])
    if not addr.Ok():
        print(f"invalid addr {addr.Err()}")
        return

    ex, dom = sys.argv[1], sys.argv[2]
    addr = addr.Val()

    name = ""
    if len(sys.argv) >= 5:
        name = sys.argv[4]

    match ex, dom:
        case ("ex1", "client"):
            import cmds.ex1.client
            cmds.ex1.client.Handle(addr)
        case ("ex1", "server"):
            import cmds.ex1.server
            cmds.ex1.server.Handle(addr)

        case ("ex2", "client"): 
            import cmds.ex2.client
            cmds.ex2.client.Handle(addr)
        case ("ex2", "server"): 
            import cmds.ex2.server
            cmds.ex2.server.Handle(addr)

        case ("ex3", "client"): 
            import cmds.ex3.client
            cmds.ex3.client.Handle(addr, name)
        case ("ex3", "server"): 
            import cmds.ex3.server
            cmds.ex3.server.Handle(addr)

        case ("ex4", "client"): 
            import cmds.ex4.client
            cmds.ex4.client.Handle(addr)
        case ("ex4", "server"): 
            import cmds.ex4.server
            cmds.ex4.server.Handle(addr)

        case ("ex10", "client"): 
            import cmds.ex10.client
            cmds.ex10.client.Handle(addr, name)
        case ("ex10", "server"): 
            import cmds.ex10.server
            cmds.ex10.server.Handle(addr)

        case _:
            print("unknown exercise")
            sys.exit(1)

if __name__ == "__main__":
    main()
