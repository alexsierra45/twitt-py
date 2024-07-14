from chord.node import ChordNode
from persistency.user import UserPersitency
from services.auth_service import start_auth_service
from config import NETWORK


# func Start(rsaPrivateKeyPath string, rsaPublicteKeyPath string, network string) {
# 	var err error

# 	rsaPrivate = rsaPrivateKeyPath
# 	rsaPublic = rsaPublicteKeyPath

# 	node, err = chord.DefaultNode()

# 	if err != nil {
# 		log.Fatalf("Can't start chord node")
# 	}

# 	port := "10000"
# 	broadListen := "11000"
# 	broadRequest := "12000"
# 	node.Start(port, broadListen, broadRequest)

# 	go StartUserService(network, "0.0.0.0:50051")
# 	go StartAuthServer(network, "0.0.0.0:50052")
# 	go StartPostsService(network, "0.0.0.0:50053")
# 	go StartFollowService(network, "0.0.0.0:50054")
# }

def start():

    node = ChordNode()

    user_persitency = UserPersitency(node)

    start_auth_service(NETWORK, "172.31.141.188:5000", user_persitency)