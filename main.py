from bitbot.algorithm import TrendFollowing
from bitbot.services import BitTrex


if __name__ == "__main__":
    b = BitTrex()
    tf = TrendFollowing(b, r"C:\Projects\bitbot\example_config.json")
    tf.run()