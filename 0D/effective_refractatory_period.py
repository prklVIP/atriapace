from setup0D import create_module
import numpy as np 
import matplotlib.pyplot as plt 

def effective_refractatory_period(ode, BCL_range, dt, erpstart=50, threshold=0.8,
                                  odepath='../ode/', scpath="../data/steadycycles/"):
    """
    Calculate the ERP for an ode model for a range of BCLs. The given model is
    paced for 50 cycles at the given S1 BCL. Then a S2 pulse of lower CL follows.
    If the peak of the resulting AP is lower than the given threshold, the cell is
    refractatory. The ERP is the smallest S2CL where the cell is not refractatory.
    """
    # Compile the ODE solver module
    if isinstance(ode, str):
        module, forward = create_module(ode, path=odepath)
    else:
        module, forward, ode = ode

    # Get model parameters and indices
    model_params = module.init_parameter_values()
    index = {}
    index['V'] = module.state_indices('V')
    index['BCL'] = module.parameter_indices('stim_period')

    ERP = erpstart
    for i, BCL in enumerate(BCL_range):
        # Set BCL
        model_params[index['BCL']] = BCL

        # S1 pacing
        try:
            init_states = np.load(scpath+"%s_BCL%d.npy" % (ode, BCL))
        except:
            print "Steady cycle at S1=%d for ODE model: %s not found." % (S1, ode)
            print "Pacing 0D cell model to find it, this may take a minute."
            states = find_steadycycle([module, forward, ode], BCL, dt, odepath=odepath, scpath=scpath)
            print "Steady cycle found, proceeding to do dynamic pacing."

        t = 0; tstop = BCL
        states = init_states.copy()
        V = [states[index['V']]]
        while t <= tstop:
            forward(states, t, dt, model_params)
            t += dt
            V.append(states[index['V']])
        Vpeak = max(V)

        # S2 pulses 
        for S2 in np.arange(ERP, BCL, 0.1):
            model_params[index['BCL']] = S2
            states = init_states.copy()

            t = 0;
            while t <= S2:
                forward(states, t, dt, model_params)
                t += dt
    
            V = [states[index['V']]]
            while t <= 2*S2:
                forward(states, t, dt, model_params)
                t += dt
                V.append(states[index['V']])

            if np.max(V) > threshold*Vpeak:
                ERP = S2
                print "S1: %f,  ERP: %f" % (BCL, ERP)
                break
            else:
            	print "S2: %f, Vpeak: %f" % (S2, np.max(V)/Vpeak)

if __name__ == '__main__':
    ode = 'FK_cAF'
    ode = 'hAM_KSMT_cAF'
    ode = 'FK_nSR'
    ode = 'hAM_KSMT_nSR'

    # BCL_range = xrange(300, 1005, 5)
    BCL_range = range(300, 1000, 5)
    dt = 0.01

    start = 50

    effective_refractatory_period(ode, BCL_range, dt, erpstart=250)