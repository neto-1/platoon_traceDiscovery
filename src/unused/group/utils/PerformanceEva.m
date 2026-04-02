clear

% Define table 
Schema = {'Edges';'Vehicles';'Iteration';'STime';'RTime';'GTime';'ITime';'VShortestPath';'PTime';'SumSP';'SumPSP';'UVehicles';'Ing';'Outg';'Optimum'; 'OptimumTime'};
T = table(0,0,0,0,0,0,0,0,0,0,0,0,0,0,-1,0);
T.Properties.VariableNames = Schema;

%%% link to current folder
% pwd;
% currentFolder = pwd;

%%%%%% gerrits pc
files = getFiles('C:\Users\db-admin\Documents\tests\res\LargeResults');
%%%%%% dimas pc
%files = getFiles('C:\Users\Dietrich\Desktop\res\Results');

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
files = getFiles('C:\Users\db-admin\Documents\tests\res\ResultsOpt');

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
    
end




for durchlaufending = 1:3
    if durchlaufending == 1
        edges =118204;
    end
    if durchlaufending == 2
        edges = 374347;
    end
    if durchlaufending == 3
        edges = 632524;
    end
    
    rows = T.Edges == edges ;

    %%%%%%%%%%%% Performance Test %%%%%%%%%%%%
    %%%%%% columns containing time
    %%% all times
    varsAllTimes = {'STime','RTime','GTime','ITime'};
    %varsAllTimes = {'RTime','GTime','ITime'};
    %%% times without LP-group-calculating
    varsScore = {'RTime'};
    %%% times without LP-group-calculating
    varsScoreGrouping = {'RTime','GTime'};
    %%% times without LP-group-calculating
    varsGrouping = {'GTime'};


    firstPerformanceAllTimes = table2array(T(rows, varsAllTimes));
    firstPerformanceScore = table2array(T(rows, varsScore));
    firstPerformanceScoreGrouping = table2array(T(rows, varsScoreGrouping));
    firstPerformanceGrouping = table2array(T(rows, varsGrouping));


    %%%%fill matrix with values
    firstTimes = zeros(length(firstPerformanceAllTimes(:,1)),4);
    for first = 1:length(firstPerformanceAllTimes(:,1))
        firstTimes(first,4) = sum(firstPerformanceAllTimes(first,:));
        firstTimes(first,1) = sum(firstPerformanceScore(first,:));
        firstTimes(first,3) = sum(firstPerformanceScoreGrouping(first,:));
        firstTimes(first,2) = sum(firstPerformanceGrouping(first,:));

    end

    firstTimes = array2table(firstTimes);
    firstTimes.Properties.RowNames = {'10';'100';'200';'30';'400';'50';'70'};
    firstTimes.Properties.VariableNames = {'ScoreTime' 'GroupingTime' 'ScoreGrouping' 'comulativeTime'};

    sortrows(firstTimes,1)
end

