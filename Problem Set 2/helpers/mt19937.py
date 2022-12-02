# This is a Pseudo Random Number Generator using the Mersene Twister Algorithm
class RandomGenerator:
    __N = 624

    def __init__(self, seed: int = None) -> None:
        self.table = [0] * RandomGenerator.__N
        self.index = RandomGenerator.__N+1
        if seed is None:
            import time
            seed = time.time_ns()
        self.seed(seed)

    def seed(self, seed: int):
        self.table[0] = seed
        for i in range(1, RandomGenerator.__N):
            temp = 1812433253 * (self.table[i-1] ^ (self.table[i-1] >> 30)) + i
            self.table[i] = temp & 0xffffffff

    def __twist(self):
        for i in range(0, RandomGenerator.__N):
            x = (self.table[i] & 0x80000000) + (self.table[(i+1) % RandomGenerator.__N] & 0x7FFFFFFF)
            xA = x >> 1
            if (x % 2) != 0:
                xA = xA ^ 0x9908B0DF
            self.table[i] = self.table[(i + 397) % RandomGenerator.__N] ^ xA

    def generate(self) -> int:
        if self.index >= RandomGenerator.__N:
            self.__twist()
            self.index = 0

        y = self.table[self.index]
        y = y ^ ((y >> 11) & 0xFFFFFFFF)
        y = y ^ ((y << 7) & 0x9D2C5680)
        y = y ^ ((y << 15) & 0xEFC60000)
        y = y ^ (y >> 18)

        self.index += 1
        return y & 0xffffffff
    
    def int(self, l: int, u: int) -> int:
        assert l <= u, f"the lower bound must be less then or equal the upper bound, got {l=} nd {u=}"
        if l == u: return l
        return l + self.generate() % (u - l + 1)

    def float(self, l: float = 0, u: float = 1) -> float:
        return (self.generate() / 0xffffffff) * (u - l) + l