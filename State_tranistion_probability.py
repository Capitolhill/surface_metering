import numpy as np
import pandas as pd

#State variables
NA = 12 #maximum number of aircraft waiting for gates 
NG = 5  #total number of gates available
NM = 6  #number of metering area slots
NR = 13 #runway queue capacity

#Action variables
tau_1, tau_2 = [i for i in range(NM+1)], [i for i in range(NM+1)] 
tau_1, tau_2 = np.array(tau_1), np.array(tau_2)

#Probability of arrivals (A_t) and pushbacks(B_t)
P_A = [0,0,0.03,0.25,0.45,0.25,0.03]
P_B = [0,0.05,0.13,0.23,0.25,0.19,0.1,0.04,0.01]

#constant corresponding to the scheduled number of departures (ND_t)
"""ND_t is a constant corresponding to the scheduled number of departures in a period. 
Thus, ND_t can be obtained based on the departure rate (24 in 1 hour --> 4 in 10 min) used. """
sch_dep = int(24/6) 



#Making transition probabilty matrix (actually dataframe) by enumerating all possibilities
next_state, tr_prob = {}, {}

for sa in range(NA+1):
    for sg in range(NG+1):
        for sm in range(NM+1):
            for sr in range(NR+1):
                for action_1 in tau_1:
                    for action_2 in tau_2:
                        for A in range(2,len(P_A)): #since first 2 arrivals (i.e. 0 & 1) have 0 probability.
                            for B in range(1,len(P_B)): #since first pushback (i.e. 0) has 0 probability.

                                temp_sa = sa - min(sa,sg) + A
                                temp_sg = sg - min(sa,sg) + min(action_1, B)
                                temp_sm = sm + min(action_1, B) - action_2
                                temp_sr = max(sr + action_2 - sch_dep, 0)

                                if (temp_sa>=0 and temp_sa<=NA) and (temp_sg>=0 and temp_sg<=NG) and (temp_sm>=0 and temp_sm<=NM) and (temp_sr>=0 and temp_sr<=NR):
                                    next_state[sa,sg,sm,sr,action_1, action_2, A , B] = (temp_sa,temp_sg,temp_sm,temp_sr)
                                    tr_prob[sa,sg,sm,sr,action_1, action_2, A , B] = P_A[A]*P_B[B]

df_ns = pd.DataFrame(list(next_state.items()),
                      columns=['current_state_extra','next_state'])
df_tp = pd.DataFrame(list(tr_prob.items()),
                      columns=['current_state_extra','probability'])

df_sm_extra = pd.merge(df_ns, df_tp, on='current_state_extra')
df_sm_extra['current_state'] = df_sm_extra['current_state_extra'].str[0:4]
df_sm_extra['action_state'] = df_sm_extra['current_state_extra'].str[4:6]
df_sm = df_sm_extra[['current_state', 'action_state', 'next_state', 'probability']]
df_sm_final = df_sm.groupby(['current_state','action_state', 'next_state']).sum()
print(df_sm_final)                        