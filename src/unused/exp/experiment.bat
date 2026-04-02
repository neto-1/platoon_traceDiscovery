@echo off

set cdir=%cd%

cd ..
cd lp
set ldir=%cd%



set pdir=%cd..%
cd %R_HOME%
cd bin


set groups=20 50 80 100 200 500
set vehicles=10 30 50 70 100 200 400

for %%v in (%vehicles%) do (
	echo %%v
	echo/
	for /L %%N IN (1, 1, 1) DO (
		Rscript %cdir%\simple.r %%v %%N  & python %ldir%\groups.py %%v %%N
	)
)

cd %cdir%

pause