from Crypto.Util.number import getRandomInteger

POLY_MASK_32 = 0xB4BCD35C
POLY_MASK_31 = 0x7A5BC2E3


class Rand:
    def __init__(self, s1=None, s2=None):
        if s1 is None:
            s1 = getRandomInteger(32)
            #print(f"correct is {(s1>>2)%4}")

        if s2 is None:
            s2 = getRandomInteger(32)

        self.lfsr32 = s1
        self.lfsr31 = s2
        self.retrand = 0

    def getRand(self):

        feedback = self.lfsr32 & 1
        self.lfsr32 >>= 1
        if feedback == 1:
            self.lfsr32 ^= POLY_MASK_32
        else:
            self.retrand ^= POLY_MASK_32

        feedback = self.lfsr32 & 1
        self.lfsr32 >>= 1
        if feedback == 1:
            self.lfsr32 ^= POLY_MASK_32
        else:
            self.retrand ^= POLY_MASK_32

        feedback = self.lfsr31 & 1
        self.lfsr31 >>= 1
        if feedback == 1:
            self.lfsr31 ^= POLY_MASK_31
        else:
            self.retrand ^= POLY_MASK_31

        # print(bin(self.lfsr32)[2:].zfill(32))
        # print(bin(self.lfsr31)[2:].zfill(32))

        return (self.lfsr32 ^ self.lfsr31) & 0xffff



class Randcrack:

    def __init__(self):
        self.og_seed_32 = 0
        self.og_seed_31 = 0
        self.step = 0

        self.values = [0]  # the first step is unknown

        self.completed = False



    def seed_step_32(self, n):
        s = self.og_seed_32

        for i in range(n):
            feedback = s & 1
            s >>= 1
            if feedback == 1:
                s ^= POLY_MASK_32

            feedback = s & 1
            s >>= 1
            if feedback == 1:
                s ^= POLY_MASK_32

        return s

    def seed_step_31(self, n):
        s = self.og_seed_31

        for i in range(n):
            feedback = s & 1
            s >>= 1
            if feedback == 1:
                s ^= POLY_MASK_31

        return s

    def reconstruct_bit(self, position, time):
        return (self.get_bit(self.values[time], position) ^
                self.get_bit(self.seed_step_31(time), position) ^
                self.get_bit(self.seed_step_32(time), position))

    def reconstruct_step(self):

        self.og_seed_32 += (self.reconstruct_bit(0, self.step) << (self.step * 2))
        self.og_seed_31 += (self.reconstruct_bit(2, self.step - 1) << (self.step + 1))
        self.og_seed_32 += (self.reconstruct_bit(1, self.step) << (self.step * 2 + 1))

    def decuce_first_step(self):
        for guess in range(4):
            self.og_seed_32 = guess << 2
            self.og_seed_31 = 0

            self.og_seed_31 += (self.get_bit(self.values[1], 0) ^ self.get_bit(self.og_seed_32, 2)) << 1
            self.og_seed_31 += (self.get_bit(self.values[1], 1) ^ self.get_bit(self.og_seed_32, 3)) << 2

            self.step +=1
            for i in range(14):
                self.og_seed_32 += (self.reconstruct_bit(i, 2) << (i + 4))
                self.og_seed_31 += (self.reconstruct_bit(i + 2, 1) << (i + 3))
            self.step -= 1


            ra = Rand(self.og_seed_32, self.og_seed_31)

            ra.getRand()
            ra.getRand()
            x = ra.getRand()
            if x & 0x3f == self.values[-1] & 0x3f:
                return guess
        else:
            print('something went wrong')

    def feed(self, number):

        self.values.append(number)
        self.step += 1

        if self.step == 1 or self.step == 2:
            return

        if self.step == 3:
            self.decuce_first_step()

        self.reconstruct_step()

        if self.step == 16:
            self.completed = True
            self.og_seed_31 &= 0xffff

            for i in range(16):
                self.og_seed_31 += self.reconstruct_bit(i, self.step) << (16 + i)

    def predict(self):

        if not self.completed:
            print('not yet')
            return

        ran = Rand(self.og_seed_32, self.og_seed_31)

        for i in range(16):
            (ran.getRand())

        return ran.getRand()

    @staticmethod
    def print_bin(n):
        print(bin(n)[2:].zfill(32))

    @staticmethod
    def get_bit(n, p):
        return n & 1 << p > 0


def main():
    for i in range(10000):
        rand = Rand()

        values = [rand.getRand() for _ in range(16)]

        r = Randcrack()

        for v in values:
            r.feed(v)

        assert r.predict() == rand.getRand()


if __name__ == '__main__':
    main()
