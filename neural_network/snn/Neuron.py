import numpy as np

class Neuron:
    def __init__(self, address, dendrites=dict(), axonTerminals=list(), 
                 histLen=60, resting=0, threshold=100, refactorPeriod=5, 
                 leak=1, inhibit=100):
        self.address        = address
        self.dendrites      = dendrites
        self.axonTerminals  = axonTerminals
        self.histLen        = histLen
        self.potential      = resting
        self.resting        = resting
        self.threshold      = threshold
        self.depressvalue   = self.threshold
        self.depressstep    = self.threshold / 100
        self.refactorPeriod = refactorPeriod
        self.leak           = leak
        self.inhibit        = inhibit
        self.history        = list()
        self.spike          = False
        self.stdpCount      = 0
        self.dwSum          = 0

    def STDP(self, address, lr, A, dt, ms):
        if (True): #(dt <= -2 or dt >= 2)):
            if (dt > 0):
                s, impact = -1, self.dendrites[address] 
            else:
                s, impact =  1, 1 - self.dendrites[address]
            dw = lr * (s*A) * np.e ** (dt / (s*ms)) * impact
            # dw = lr * s*dt * impact
            self.dendrites[address] += dw
            self.dwSum += dw if (dw > 0) else -dw


    def inputSpike(self, address, train=True):
        if (self.stdpCount < (self.histLen - self.refactorPeriod)):
            # Update potential, ...
            if (address not in self.dendrites.keys()):
                self.potential -= self.inhibit
            else:
                self.potential += self.dendrites[address]
                if (train):
                    # ... history, ...
                    self.history.append([address, 0])
                    for i, [address, dt] in enumerate(self.history):
                        if(dt < -self.histLen):
                            del self.history[i]
                        else: break
                    # ... and stdpCount.
                    if (self.stdpCount > 0):
                        dt = self.histLen - self.stdpCount
                        self.STDP(address, 0.01, 0.1, dt, self.histLen/2) # Postsynaptic Potential

    def outputSpike(self, train=True):
        if (self.potential >= self.threshold):
            if (train):
                for address, dt in self.history:
                    self.STDP(address, 0.01, 0.3, dt, self.histLen)      # Presynaptic Potential
                acc = sum(self.dendrites.values())
                for k, dv in self.dendrites.items():
                    self.dendrites[k] = (392 - self.dwSum) * (dv / (acc))
                self.stdpCount = self.histLen
                self.history = list()
            self.potential = self.resting
            self.spike = True
            return self.spike

    def timeStep(self, train=True):
        if (not self.spike):
            df = self.potential - self.resting
            if (df != 0):
                self.potential -= self.leak if (df > self.leak) else df
            if (train):
                if (self.stdpCount > 0):
                    self.stdpCount -= 1
                for i, _ in enumerate(self.history):
                    self.history[i][1] -= 1
        #        if (self.depressvalue >= self.threshold*10):
        #            self.depressvalue -= self.depressstep
        #            self.threshold -= 0.1
        # else:
        #     self.threshold *= 1.2
        self.spike = False
