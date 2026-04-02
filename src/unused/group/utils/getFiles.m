function name = getFiles(pathName)
    [stat path]=dos(['dir ' pathName '\*.txt /s /B >path.txt'] );
    name=importdata('path.txt');
    delete path.txt;
end