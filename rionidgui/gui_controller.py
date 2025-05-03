from numpy import argsort, where, append
from loguru import logger
from rionid.importdata import ImportData
from barion.amedata import AMEData
import time
def import_controller(datafile=None, filep=None, alphap=None, refion=None, highlight_ions=None, harmonics = None, nions = None, amplitude=None, circumference = None, mode=None, sim_scalingfactor=None, value=None, reload_data=None,peak_threshold_pct = None,min_distance=None,output_results=None,saved_data = None):
    try:
        start_time = time.time()  # Record start time for each test_alphap iteration
        # initializations
        if float(alphap) > 1: alphap = 1/float(alphap)**2 # handling alphap and gammat
        fref = brho = ke = gam = None
        if mode == 'Frequency': fref = float(value)
        elif mode == 'Bρ': brho = float(value)
        elif mode == 'Kinetic Energy': ke = float(value)
        elif mode == 'Gamma': gam = float(value)
        # Calculations | ImportData library
        mydata = ImportData(refion, highlight_ions, float(alphap), filename = datafile, reload_data = reload_data, circumference = circumference,peak_threshold_pct=peak_threshold_pct,min_distance=min_distance)
        end_time1 = time.time()  # Record end time after each iteration
        elapsed_time1 = end_time1 - start_time  # Calculate elapsed time for this iteration
        
        if reload_data: 
            mydata._set_particles_to_simulate_from_file(filep,verbose=output_results)
            mydata._calculate_moqs()
        else:
            mydata.ame = saved_data.ame
            mydata.ame_data = saved_data.ame_data
            mydata.particles_to_simulate = saved_data.particles_to_simulate
            mydata.moq = saved_data.moq
            mydata.total_mass = saved_data.total_mass

        

        mydata._calculate_srrf(fref = fref, brho = brho, ke = ke, gam = gam, correct = False)

        harmonics = [float(h) for h in harmonics.split()]
        mydata._simulated_data(brho = brho, harmonics = harmonics, mode = mode, sim_scalingfactor = sim_scalingfactor, nions = nions) # -> simulated frecs
        # "Outputs"
        if nions:
            display_nions(int(nions), mydata.yield_data, mydata.nuclei_names, mydata.simulated_data_dict, refion, harmonics)
        if output_results:
            logger.info(f'Simulation results (ordered by frequency) will be saved to simulation_result.out')
        sort_index = argsort(mydata.srrf)
        # Save the results to a file with the specified format
        # Save the results if output_results is True
        if output_results:
            save_simulation_results(mydata,mode, harmonics, sort_index)
            logger.info(f'Succesfully saved!')

        return mydata # Returns the simulated spectrum data 
    
    except Exception as e:
        print(f"Error during calculations: {str(e)}")
        return None

def display_nions(nions, yield_data, nuclei_names, simulated_data_dict, ref_ion, harmonics):
    sorted_indices = argsort(yield_data)[::-1][:nions]
    ref_index = where(nuclei_names == ref_ion)[0]
    if ref_index not in sorted_indices:
        sorted_indices = append(sorted_indices, ref_index)
    nuclei_names = nuclei_names[sorted_indices]
    
    for harmonic in harmonics: # for each harmonic
        name = f'{harmonic}'
        simulated_data_dict[name] = simulated_data_dict[name][sorted_indices]

def save_simulation_results(mydata, mode, harmonics, sort_index, filename = 'simulation_result.out'):
    """
    Saves the simulation results to a specified file.
    
    Parameters:
    - filename: str, the name of the file to save the results.
    - mydata: ImportData object, contains the calculated simulation data.
    - harmonics: list of floats, the harmonic numbers used in the simulation.
    - sort_index: list of indices, sorted indices of the simulated results by frequency.
    """
    with open(filename, 'w') as file:
        # Writing harmonics and brho information
        brho = mydata.brho
        for harmonic in harmonics:
            header0 = f'Harmonic: {harmonic} , Bp: {brho:.6f} [Tm]'
            logger.info(header0)
            file.write(header0 + '\n')
        
        # Writing the header for the data table
        header1 = f"{'ion':<15}{'fre[Hz]':<30}{'yield [pps]':<15}{'m/q [u]':<15}{'m [eV]':<15}"
        file.write(header1 + '\n')
        file.write('-' * len(header1) + '\n')
        logger.info(header1)
        
        # Writing the sorted simulation results
        for i in sort_index:
            ion = mydata.nuclei_names[i]
            if mode == 'Frequency': fre = mydata.srrf[i] * mydata.ref_frequency
            elif mode == 'Bρ': fre = mydata.srrf[i] * mydata.ref_frequency*harmonic
            yield_ = mydata.yield_data[i]
            moq = mydata.moq[ion]
            mass_u = mydata.total_mass[ion]
            mass = AMEData.to_mev(mass_u) * 1e6
            result_line = f"{ion:<15}{fre:<30.10f}{yield_:<15.4e}{moq:<15.12f}{mass:<15.3f}"
            logger.info(result_line)
            file.write(result_line + '\n')
