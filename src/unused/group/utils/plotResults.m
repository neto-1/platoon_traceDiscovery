clear

% Define table 
Schema = {'Edges';'Vehicles';'Iteration';'STime';'RTime';'GTime';'ITime';'VShortestPath';'PTime';'SumSP';'SumPSP';'UVehicles';'Ing';'Outg';'Optimum'; 'OptimumTime'};
T = table(0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0);
T.Properties.VariableNames = Schema;

%%% link to current folder
% pwd;
% currentFolder = pwd;

%%%%%% gerrits pc
%files = getFiles('C:\Users\db-admin\Documents\tests\res\Results');

%%%%%% dimas pc
files = getFiles('C:\Users\Dietrich\Desktop\desk\res\Results');

for n = 1:numel(files)
    file = files(n);
    fid = fopen(char(file));

    % first line of txt file
    tline = fgets(fid);
    i = 1;
    A=zeros(1,16);
    while ischar(tline)
        A(i) = str2double(tline);
        %disp(tline);
        tline = fgets(fid);
        i=1+i;
    end
    % add new row with data 
    %A(i+1)=-1;
    C = num2cell(A);
    T(n:n,:)= C;
    fclose(fid);
end

%close the opened txt files (or matlab crash
fclose('all');

T = sortrows(T,'Edges');
%T{:,{'Edges','GTime'}};

%plotTable(T)


%%%%%% gerrits pc
files = getFiles('C:\Users\Dietrich\Desktop\res\ResultsOpt');

%%%%%% dimas pc
%files = getFiles('C:\Users\Dietrich\Desktop\res\ResultsOpt');

for n = 1:numel(files)
    file = files(n);
    fid = fopen(char(file));

    % first line of txt file
    tline = fgets(fid);
    i=0;

    A=zeros(1,2);
    while ischar(tline)
        switch i
            case 0
                edges = str2double(tline);
            case 1
                %disp('vehicles');
                vehicles = str2double(tline);
            case 2
                %disp('iteration');
                time = str2double(tline);
            case 3
                %disp('match vehicle')
                opt = str2double(tline);
        end
        tline = fgets(fid);
        i=1+i;
      
    end
    
%close the opened txt files (or matlab crash
fclose('all');
    
    rows = T.Edges == edges & T.Vehicles == vehicles;
    vars = {'Optimum','OptimumTime'};
    edges;
    vehicles;
    time;
    opt;
    
    tableA = table(0,0);
    for d = 1:height(T(rows, vars))
       tableA(d,:) = table(opt,time);
    end

    tableA;
    T(rows, vars);
    T(rows, vars) = tableA;
    
end


T

%plotTable(T)

