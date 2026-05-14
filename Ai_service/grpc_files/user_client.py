import grpc
from grpc_files import user_pb2, user_pb2_grpc

def get_user_from_grpc(user_id):
    try:
        channel = grpc.insecure_channel("stayease_web:50051")
        stub = user_pb2_grpc.UserServiceStub(channel)

        response = stub.GetUser(
            user_pb2.GetUserRequest(user_id=int(user_id)),
            timeout=5
        )
        return {
            "id": response.id,
            "username": response.username,
            "email": response.email,
            "role": response.role,
        }

    except grpc.RpcError:
        return None