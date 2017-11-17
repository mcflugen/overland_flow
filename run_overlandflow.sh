#!/bin/bash

#SBATCH --array 1-223
#SBATCH --nodes 1
#SBATCH --time=01:00:00
##SBATCH --qos blanca-csdms
##SBATCH --partition=blanca-csdms
#SBATCH --ntasks 1
#SBATCH --job-name=overlandflow


module purge

WORKDIR="/projects/huttone/jobs"
rundir="$WORKDIR/$SLURM_ARRAY_TASK_ID"

FILES_TO_STAGE="\
  scripts/extract_infiltration.py \
  data/params-iowa.yaml \
  data/iowa_square.asc \
  data/rain_days.csv"

mkdir -p $rundir
cp $FILES_TO_STAGE $rundir
cd $rundir

mm_per_day=$(sed "${SLURM_ARRAY_TASK_ID}q;d" ./rain_days.csv)
m_per_s=$(python -c "print($mm_per_day * 1e-3 / (60. * 60.))")
echo $mm_per_day > rain.txt

overlandflow --verbose ./params-iowa.yaml \
    --set rain_step_function.magnitude=$m_per_s \
    --output=overland_flow-${SLURM_ARRAY_TASK_ID}.nc \
    --fields=soil_water_infiltration__depth \
    --fields=surface_water__depth \
    --fields=topographic__elevation && \
python ./extract_infiltration.py \
    overland_flow-${SLURM_ARRAY_TASK_ID}.nc $mm_per_day > summary.txt
