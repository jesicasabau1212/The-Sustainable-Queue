import pandas as pd
import numpy as np


class SustainableQueue:

    def __init__(self, server_capacity, carbon_intensities, max_wait=48, mid_wait=24, short_wait=12, p_low=25, p_mid=50, p_high=75, conversion_factor=0.0005):

        self.capacity = server_capacity
        self.HS23_to_kW = conversion_factor

        self.t_low = np.percentile(carbon_intensities, p_low)
        self.t_mid = np.percentile(carbon_intensities, p_mid)
        self.t_high = np.percentile(carbon_intensities, p_high)

        self.max_wait = max_wait
        self.mid_wait = mid_wait
        self.short_wait = short_wait

        self.waiting_line = []
        self.log = []
        self.completed_jobs_stats = []

    def step(self, current_hour, new_jobs, current_carbon):

        if new_jobs > 0:
            self.waiting_line.append({
                'hour_arrived': current_hour, 'size': new_jobs,
            })

        run_now = []
        wait_longer = []

        for bucket in self.waiting_line:
            hours_waiting = current_hour - bucket['hour_arrived']

            if hours_waiting >= self.max_wait:
                bucket['reason'] = 'Deadline (Forced)'
                run_now.append(bucket)
            elif hours_waiting >= self.mid_wait and current_carbon <= self.t_high:
                bucket['reason'] = 'High Carbon (<75th)'
                run_now.append(bucket)
            elif hours_waiting >= self.short_wait and current_carbon <= self.t_mid:
                bucket['reason'] = 'Medium Carbon (<50th)'
                run_now.append(bucket)
            elif current_carbon <= self.t_low:
                bucket['reason'] = 'Low Carbon (<25th)'
                run_now.append(bucket)
            else:
                wait_longer.append(bucket)

        run_now.sort(key=lambda x: x['hour_arrived'])

        space_left = self.capacity
        done_this_hour_hs23 = 0
        done_low = done_medium = done_high = done_deadline = 0
        leftover_jobs= []

        for bucket in run_now:
            if space_left <= 0:
                leftover_jobs.append(bucket)
                continue

            executed = min(bucket['size'], space_left)
            space_left -= executed
            bucket['size'] -= executed

            if bucket['size'] > 0:
                leftover_jobs.append(bucket)

            done_this_hour_hs23 += executed

            reason = bucket['reason']
            if reason == 'Low Carbon (<25th)': done_low += executed
            elif reason == 'Medium Carbon (<50th)': done_medium += executed
            elif reason == 'High Carbon (<75th)': done_high += executed
            elif reason == 'Deadline (Forced)': done_deadline += executed

            self.completed_jobs_stats.append({
                'Wait_Time_Hours':  current_hour - bucket['hour_arrived'],
                'Workload_Size': executed,
                'Execution_Reason': reason,
            })

        self.waiting_line = leftover_jobs + wait_longer

        total_waiting_now = sum(b['size'] for b in self.waiting_line)
        done_kW = done_this_hour_hs23 * self.HS23_to_kW

        self.log.append({
            'Hour': current_hour,
            'Demand_In_HS23': new_jobs,
            'Executed_kW': done_kW,
            'Waiting_in_Queue_HS23': total_waiting_now,
            'Current_Carbon_g_per_kWh': current_carbon,
            'Carbon_Emissions_gCO2': done_kW * current_carbon,
            'Executed_Low_Carbon_kW': done_low * self.HS23_to_kW,
            'Executed_Medium_Carbon_kW': done_medium * self.HS23_to_kW,
            'Executed_High_Carbon_kW': done_high * self.HS23_to_kW,
            'Executed_Deadline_kW': done_deadline * self.HS23_to_kW,
        })

    def get_results_df(self):
        return pd.DataFrame(self.log)

    def get_wait_times_df(self):
        return pd.DataFrame(self.completed_jobs_stats)
