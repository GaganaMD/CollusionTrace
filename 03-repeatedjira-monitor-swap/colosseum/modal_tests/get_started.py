import modal

app = modal.App("gagana-modal-test")


@app.function()
def square(x):
    print("This code is running on a Modal worker!")
    return x**2


@app.local_entrypoint()
def main():
    print("The square is", square.remote(42))