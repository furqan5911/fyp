from blinker import Namespace

# Create a namespace for signals
namespace = Namespace()

# Define a signal for accident detection
accident_detected_signal = namespace.signal('accident-detected')
