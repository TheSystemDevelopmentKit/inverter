"""
========
Inverter
========

Inverter model template The System Development Kit
Used as a template for all TheSyDeKick Entities.

Current docstring documentation style is Numpy
https://numpydoc.readthedocs.io/en/latest/format.html

For reference of the markup syntax
https://docutils.sourceforge.io/docs/user/rst/quickref.html

This text here is to remind you that documentation is important.
However, youu may find it out the even the documentation of this 
entity may be outdated and incomplete. Regardless of that, every day 
and in every way we are getting better and better :).

Initially written by Marko Kosunen, marko.kosunen@aalto.fi, 2017.


Role of section 'if __name__=="__main__"'
--------------------------------------------

This section is for self testing and interfacing of this class. The content of
it is fully up to designer. You may use it for example to test the
functionality of the class by calling it as ``pyhon3.6 __init__.py`` or you may
define how it handles the arguments passed during the invocation. In this
example it is used as a complete self test script for all the simulation models
defined for the inverter. 

"""

import os
import sys
if not (os.path.abspath('../../thesdk') in sys.path):
    sys.path.append(os.path.abspath('../../thesdk'))

from thesdk import *
from rtl import *
from spice import *

import numpy as np

class inverter(rtl,spice,thesdk):
    @property
    def _classfile(self):
        return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__

    def __init__(self,*arg): 
        """ Inverter parameters and attributes
            Parameters
            ----------
                *arg : 
                If any arguments are defined, the first one should be the parent instance

            Attributes
            ----------
            proplist : array_like
                List of strings containing the names of attributes whose values are to be copied 
                from the parent

            Rs : float
                Sampling rate [Hz] of which the input values are assumed to change. Default: 100.0e6

            vdd : float
                Supply voltage [V] for inverter analog simulation. Default 1.0.

            IOS : Bundle
                Members of this bundle are the IO's of the entity. See documentation of thsdk package.
                Default members defined as

                self.IOS.Members['A']=IO() # Pointer for input data
                self.IOS.Members['Z']= IO() # pointer for oputput data
                self.IOS.Members['control_write']= IO() # Piter for control IO for rtl simulations

            model : string
                Default 'py' for Python. See documentation of thsdk package for more details.

        """
        self.print_log(type='I', msg='Initializing %s' %(__name__)) 
        self.proplist = ['Rs'] # Properties that can be propagated from parent
        self.Rs = 100e6 # Sampling frequency
        self.vdd = 1.0
        self.IOS=Bundle()
        self.IOS.Members['A'] = IO() # Pointer for input data
        self.IOS.Members['Z'] = IO()
        self.IOS.Members['CLK'] = IO() # Test clock for spice simulations
        self.IOS.Members['control_write'] = IO() # File for control is created in controller
        self.model = 'py' # Can be set externally, but is not propagated

        # this copies the parameter values from the parent based on self.proplist
        if len(arg)>=1:
            parent=arg[0]
            self.copy_propval(parent,self.proplist)
            self.parent=parent

        self.init()

    def init(self):
        """ Method to re-initialize the structure if the attribute values are changed after creation.

        """
        pass #Currently nothing to add

    def main(self):
        ''' The main python description of the operation. Contents fully up to designer, however, the 
        IO's should be handled bu following this guideline:
        
        To isolate the internal processing from IO connection assigments, 
        The procedure to follow is
        1) Assign input data from input to local variable
        2) Do the processing
        3) Assign local variable to output

        '''
        inval=self.IOS.Members['A'].Data
        out=np.array(1-inval)
        if self.par:
            self.queue.put(out)
        self.IOS.Members['Z'].Data=out

    def run(self,*arg):
        ''' The default name of the method to be executed. This means: parameters and attributes 
            control what is executed if run method is executed. By this we aim to avoid the need of 
            documenting what is the execution method. It is always self.run. 

            Parameters
            ----------
            *arg :
                The first argument is assumed to be the queue for the parallel processing defined in the parent, 
                and it is assigned to self.queue and self.par is set to True. 
        
        '''
        if self.model=='py':
            self.main()
        else: 
            # This defines contents of modelsim control file executed when interactive_rtl = True
            interactive_control_contents="""
                add wave -position insertpoint \\
                sim/:tb_inverter:A \\
                sim/:tb_inverter:initdone \\
                sim/:tb_inverter:clock \\
                sim/:tb_inverter:Z
                run -all
                wave zoom full
            """
            if self.model=='sv':
                # Verilog simulation options here
                _=rtl_iofile(self, name='A', dir='in', iotype='sample', ionames=['A'], datatype='sint') # IO file for input A
                _=rtl_iofile(self, name='Z', dir='out', iotype='sample', ionames=['Z'], datatype='sint')
                self.rtlparameters=dict([ ('g_Rs',self.Rs),]) # Defines the sample rate
                self.interactive_control_contents=interactive_control_contents
                self.run_rtl()
                self.IOS.Members['Z'].Data=self.IOS.Members['Z'].Data[:,0].astype(int).reshape(-1,1)
            elif self.model=='vhdl':
                # VHDL simulation options here
                _=rtl_iofile(self, name='A', dir='in', iotype='sample', ionames=['A']) # IO file for input A
                _=rtl_iofile(self, name='Z', dir='out', iotype='sample', ionames=['Z'], datatype='int')
                self.rtlparameters=dict([ ('g_Rs',self.Rs),]) # Defines the sample rate
                self.interactive_control_contents=interactive_control_contents
                self.run_rtl()
                self.IOS.Members['Z'].Data=self.IOS.Members['Z'].Data.astype(int).reshape(-1,1)
            elif self.model in ['eldo','spectre','ngspice']:

                # Creating a clock signal, which is used for testing the sample output features
                _=spice_iofile(self, name='CLK', dir='in', iotype='sample', ionames='CLK', rs=2*self.Rs, \
                               vhi=self.vdd, trise=1/(self.Rs*8), tfall=1/(self.Rs*8))
                # Sample type input
                _=spice_iofile(self, name='A', dir='in', iotype='sample', ionames='A', rs=self.Rs, \
                               vhi=self.vdd, trise=1/(self.Rs*4), tfall=1/(self.Rs*4))

                ##Analog output for inverter
                self.IOS.Members['Z_ANA'] = IO()
                _=spice_iofile(self, name='Z_ANA', dir='out', iotype='event', sourcetype='V', ionames='Z')
                
                # Sample type output
                # Clock is used to sample the waveform in analog simulation
                _=spice_iofile(self, name='Z', dir='out', iotype='sample', ionames='Z', trigger='CLK', \
                               vth=self.vdd/2,edgetype='rising',ioformat='dec')
                

                # Saving the analog waveform of the input as well
                self.IOS.Members['A_OUT'] = IO()
                _=spice_iofile(self, name='A_OUT', dir='out', iotype='event', sourcetype='V', ionames='A')

                ## Extracting rising edges from the output waveform
                self.IOS.Members['Z_RISE'] = IO()
                _=spice_iofile(self, name='Z_RISE', dir='out', iotype='time', sourcetype='V', ionames='Z', \
                               edgetype='rising',vth=self.vdd/2)


                ## Extracting values of A and Z at falling edges of CLK in decimal format (integer, in this case 0 or 1)
                ## The clock signal can be any node voltage in the simulation
                self.IOS.Members['A_DIG'] = IO()
                _=spice_iofile(self, name='A_DIG', dir='out', iotype='sample', ionames='A', trigger='CLK', \
                               vth=self.vdd/2,edgetype='rising',ioformat='dec')

                # Multithreading, options and parameters
                self.nproc = 2
                self.spiceoptions = {
                            'eps': '1e-6'
                        }
                self.spiceparameters = {
                            'exampleparam': '0'
                        }

                # Defining library options
                # Path to model libraries needs to be defined in TheSDK.config as
                # either ELDOLIBFILE or SPECTRELIBFILE. In this case, no model libraries
                # will be included (assuming these variables are not defined). The
                # temperature will be set regardless.
                self.spicecorner = {
                            'corner': 'top_tt',
                            'temp': 27,
                        }

                # Example of defining supplies (not used here because the example inverter has no supplies)
                _=spice_dcsource(self,name='supply',value=self.vdd,pos='VDD',neg='VSS',extract=True)
                _=spice_dcsource(self,name='ground',value=0,pos='VSS',neg='0')

                # Adding a resistor between VDD and VSS to demonstrate power consumption extraction
                # This also demonstrates how to inject manual commands in to the testbench
                if self.model=='spectre':
                    self.spicemisc.append('simulator lang=spice')
                self.spicemisc.append('Rtest VDD VSS 2000')
                if self.model=='spectre':
                    self.spicemisc.append('simulator lang=spectre')
                
                # Plotting nodes for interactive waveform viewing.
                # Spectre also supported, but without 'v()' specifiers.
                # i.e. plotlist = ['A','Z']
                if self.model == 'eldo':
                    plotlist = ['v(A)','v(Z)']
                elif self.model == 'spectre':
                    plotlist = ['A','Z']
                else:
                    plotlist = []

                # Simulation command
                _=spice_simcmd(self,sim='tran',plotlist=plotlist)
                self.run_spice()

            if self.par:
                self.queue.put(self.IOS.Members)

    def define_io_conditions(self):
        '''This overloads the method called by run_rtl method. It defines the read/write conditions for the files

        '''
        # Input A is read to verilog simulation after 'initdone' is set to 1 by controller
        self.iofile_bundle.Members['A'].verilog_io_condition='initdone'
        # Output is read to verilog simulation when all of the outputs are valid, 
        # and after 'initdone' is set to 1 by controller
        self.iofile_bundle.Members['Z'].verilog_io_condition_append(cond='&& initdone')


if __name__=="__main__":
    import matplotlib.pyplot as plt
    from inverter import *
    from inverter.controller import controller as inverter_controller
    import pdb
    length=2**8
    rs=100e6
    indata=np.random.randint(2,size=length).reshape(-1,1)
    clk=np.array([0 if i%2==0 else 1 for i in range(2*len(indata))]).reshape(-1,1)
    controller=inverter_controller()
    controller.Rs=rs
    #controller.reset()
    #controller.step_time()
    controller.start_datafeed()

    #models=['py','sv','vhdl','eldo','spectre']
    models=['ngspice']
    duts=[]
    for model in models:
        d=inverter()
        duts.append(d) 
        d.model=model
        d.Rs=rs
        # Enable debug messages
        #d.DEBUG = True
        # Run simulations in interactive modes to monitor progress/results
        #d.interactive_spice=True
        #d.interactive_rtl=True
        # Preserve the IO files or simulator files for debugging purposes
        d.preserve_iofiles = True
        d.preserve_spicefiles = True
        # Save the entity state after simulation
        #d.save_state = True
        #d.save_database = True
        # Optionally load the state of the most recent simulation
        #d.load_state = 'latest'
        d.IOS.Members['A'].Data=indata
        d.IOS.Members['CLK'].Data=clk
        d.IOS.Members['control_write']=controller.IOS.Members['control_write']
        d.init()
        d.run()

    for k in range(len(duts)):
        hfont = {'fontname':'Sans'}
        nsamp = 20
        x = np.arange(nsamp).reshape(-1,1)
        if duts[k].model == 'eldo' or duts[k].model=='spectre' or duts[k].model=='ngspice':
            figure,axes = plt.subplots(2,2,sharex='col',tight_layout=True)
            axes[0,0].stem(x,duts[k].IOS.Members['A_DIG'].Data[:nsamp,0])
            axes[0,0].set_ylabel('Input', **hfont,fontsize=18)
            axes[0,0].grid(True)
            axes[1,0].stem(x,duts[k].IOS.Members['Z'].Data[:nsamp,0])
            axes[1,0].set_xlim(0,nsamp-1)
            axes[1,0].set_ylabel('Output', **hfont,fontsize=18)
            axes[1,0].set_xlabel('Sample', **hfont,fontsize=18)
            axes[1,0].grid(True)
            axes[0,1].plot(duts[k].IOS.Members['A_OUT'].Data[:,0],duts[k].IOS.Members['A_OUT'].Data[:,1],label='Input')
            axes[0,1].grid(True)
            axes[1,1].plot(duts[k].IOS.Members['Z_ANA'].Data[:,0],duts[k].IOS.Members['Z_ANA'].Data[:,1],label='Output')
            axes[1,1].plot(duts[k].IOS.Members['Z_RISE'].Data[:,0],np.ones(duts[k].IOS.Members['Z_RISE'].Data[:,0].shape)*duts[k].vdd/2,\
                           ls='None',marker='o',label='Rising edges')
            axes[1,1].set_xlabel('Time (s)', **hfont,fontsize=18)
            axes[1,1].set_xlim(0,(nsamp-1)/rs)
            axes[1,1].grid(True)
        else:
            if duts[k].model == 'sv' or duts[k].model == 'vhdl':
                latency=1
            else:
                latency=0
            figure,axes=plt.subplots(2,1,sharex=True)
            axes[0].stem(x,duts[k].IOS.Members['A'].Data[:nsamp,0])
            axes[0].set_ylim(0, 1.1)
            axes[0].set_xlim((np.amin(x), np.amax(x)))
            axes[0].set_ylabel('Input', **hfont,fontsize=18)
            axes[0].grid(True)
            axes[1].stem(x,duts[k].IOS.Members['Z'].Data[latency:nsamp+latency,0])
            axes[1].set_ylim(0, 1.1)
            axes[1].set_xlim((np.amin(x), np.amax(x)))
            axes[1].set_ylabel('Output', **hfont,fontsize=18)
            axes[1].set_xlabel('Sample (n)', **hfont,fontsize=18)
            axes[1].grid(True)
        titlestr = "Inverter model %s" %(duts[k].model) 
        plt.suptitle(titlestr,fontsize=20)
        plt.grid(True)
        plt.show(block=False)
        printstr="../inv_%s.eps" %(duts[k].model)
        figure.savefig(printstr, format='eps', dpi=300)
    # This is here to keep the images visible
    # For batch execution, you should comment the following line 
    input()
