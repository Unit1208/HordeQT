from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import requests
import queue

class ApiWorker(QObject):
    result_ready = pyqtSignal(object)  # Custom signal to emit the result
    error_occurred = pyqtSignal(str)   # Custom signal to emit errors

    def __init__(self, request_queue):
        super().__init__()
        self.request_queue = request_queue
        self.running = True

    @pyqtSlot()
    def process_requests(self):
        while self.running:
            try:
                # Get the next request from the queue
                method, url, params = self.request_queue.get(block=True)

                # Perform the API request
                response = requests.request(method, url, params=params)

                # Emit the result signal with the response
                self.result_ready.emit(response.json())

            except requests.RequestException as e:
                # Emit an error signal if something goes wrong
                self.error_occurred.emit(str(e))

    def stop(self):
        self.running = False

class ApiManager(QObject):
    def __init__(self):
        super().__init__()
        self.request_queue = queue.Queue()

        # Create the worker and thread
        self.worker = ApiWorker(self.request_queue)
        self.thread = QThread()
        
        # Move the worker to the thread
        self.worker.moveToThread(self.thread)
        
        # Connect signals and slots
        self.thread.started.connect(self.worker.process_requests)
        self.worker.result_ready.connect(self.handle_result)
        self.worker.error_occurred.connect(self.handle_error)

        # Start the thread
        self.thread.start()

    def add_request(self, method, url, params=None):
        self.request_queue.put((method, url, params))

    def handle_result(self, result):
        print("Received result:", result)

    def handle_error(self, error):
        print("Error occurred:", error)

    def stop(self):
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()

# Usage Example
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])

    manager = ApiManager()
    
    # Example API requests
    manager.add_request('GET', 'https://jsonplaceholder.typicode.com/posts', params={'userId': 1})
    manager.add_request('GET', 'https://jsonplaceholder.typicode.com/comments', params={'postId': 1})

    # Stop the thread after some time
    QTimer.singleShot(5000, manager.stop)

    app.exec_()
