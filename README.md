# overland_flow
landlab model that couples overland flow and infiltration


# The Workflow

This is running on our cluster, which uses slurm,

    $ module load netcdf/netcdf4-4.4.2_gcc-4.9.2
    $ module load slurm/blanca

Run all the storm days,

    $ sbatch run_overland_flow.sh

Build a summary table of all the runs,

    $ ./merge_summaries.sh > merged.txt

Map values from a particular index into a DSSAT input file,

    $ ./build_mapper.py merged.txt 1032 | ./map_values.py USAM8031.WTH
