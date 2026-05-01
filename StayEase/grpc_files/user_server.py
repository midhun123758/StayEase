import os
import sys
import django
import grpc
from concurrent import futures

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StayEase.settings")
django.setup()
from App.models import User
from grpc_files import user_pb2, user_pb2_grpc

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        try:
            user = User.objects.get(id=request.user_id)

            return user_pb2.GetUserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
            )

        except User.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return user_pb2.GetUserResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)

    server.add_insecure_port("[::]:50051")
    server.start()

    print("gRPC User server running on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()