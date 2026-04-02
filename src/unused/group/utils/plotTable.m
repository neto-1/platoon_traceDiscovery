function plotTable(T)


%%%%%%%%%%%%%%%%%%%%%%% output %%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%% specify the test cases
%%% GRAPH: 5013 = Saarland; 9819 = Thüringen; 41074 = Nds; 75738 = NRW
edges = 5013;

%%%%%%%%% vehicles: 10, 30, 50 ,70
vehicles = 10;

%%%%%%%%% variables
vars = {'Optimum','OptimumTime'};
%rows = T.Edges == edges & T.Vehicles == vehicles;
rows = T.Edges == edges ;
vars = {'Optimum','OptimumTime'};

% vehicles;
% time;
%opt;

% tableA = table(0,0);
% for d = 1:height(T(rows, vars))
%     tableA(d,:) = table(opt,time);
% end
% 
% tableA;
T(rows, vars);
% T(rows, vars) = tableA;



%%%%%%%%%%%%%%% number of "successful" and "failed" groups %%%%%%%%%%%%%%%
%vars = {'Ing','Outg'};
numberOfGroups = table2array(T(:, 'Ing'));
numberOfNotUsedGroups = table2array(T(:, 'Outg'));
Y=0;

for succGroups = 1:length(numberOfGroups(:))
    if numberOfNotUsedGroups(succGroups) == 0
        X = 0;
    else
        X = numberOfNotUsedGroups(succGroups) / numberOfGroups(succGroups);
    end
    Y = Y + X;
end
percentageOfSuccGroups = 1- (Y / succGroups);
percentageOfSuccGroups
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%% = Saarland = %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
edges = 5013;
rows = T.Edges == edges ;

%%%%%%%%%%%% Performance Test %%%%%%%%%%%%
%%%%%% columns containing time
%%% all times
varsAllTimes = {'STime','RTime','GTime','ITime','PTime'};
%%% times without LP-group-calculating
varsWithoutLP = {'STime','RTime','GTime','ITime'};
%%% times without LP-group-calculating
varsOnlyGrouping = {'RTime','GTime'};
%%% times without LP-group-calculating
varsOnlyLP = {'PTime'};
%%% time for the LP solving the whole Problem 
varsLPtime = {'OptimumTime'};

% change table to array to make the sums
SaarlandPerformanceAllTimes = table2array(T(rows, varsAllTimes));
SaarlandPerformanceWithoutLP = table2array(T(rows, varsWithoutLP));
SaarlandPerformanceOnlyGrouping = table2array(T(rows, varsOnlyGrouping));
SaarlandPerformanceOnlyLP = table2array(T(rows, varsOnlyLP));
SaarlandPerformanceLPtime = table2array(T(rows, varsLPtime));


% fill matrix with values
SaarlandTimes = zeros(length(SaarlandPerformanceAllTimes(:,1)),5);
for PerfSaarl = 1:length(SaarlandPerformanceAllTimes(:,1))
    SaarlandTimes(PerfSaarl,1) = sum(SaarlandPerformanceAllTimes(PerfSaarl,:));
    SaarlandTimes(PerfSaarl,2) = sum(SaarlandPerformanceWithoutLP(PerfSaarl,:));
    SaarlandTimes(PerfSaarl,3) = sum(SaarlandPerformanceOnlyGrouping(PerfSaarl,:));
    SaarlandTimes(PerfSaarl,4) = sum(SaarlandPerformanceOnlyLP(PerfSaarl,:));
    SaarlandTimes(PerfSaarl,5) = SaarlandPerformanceLPtime(PerfSaarl,:);
end

% names for output
SaarlandTimes = array2table(SaarlandTimes);
SaarlandTimes.Properties.RowNames = {'10';'30';'50';'70'};
SaarlandTimes.Properties.VariableNames = {'allTimes' 'withoutLP' 'OnlyGrouping' 'OnlyLP' 'LPTime'};

% output
SaarlandTimes
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%% Savings Test %%%%%%%%%%%%
% the real optimum calculated by LP for whole Problem
varsRealOptimum = {'Optimum'};
% the sum of the shortestPath of all vehicles
varsAllShortestPath = {'VShortestPath'};
% the sum of the shortest path of the assigned vehicles
varsShortestPath = {'SumSP'};
%the platooned distance of the assigned vehicles
varsShortestPathPlatoon = {'SumPSP'};



% change table to array to make the sums
SaarlandSavingsOptimum = table2array(T(rows,varsRealOptimum));
SaarlandAllSavingsShortestPath = table2array(T(rows,varsAllShortestPath));
SaarlandSavingsShortestPath = table2array(T(rows,varsShortestPath));
SaarlandSavingsShortestPathPlatoon = table2array(T(rows,varsShortestPathPlatoon));

% fill matrix with values
SaarlandSavings = zeros(length(SaarlandSavingsOptimum(:,1)),4);
for SaveSaarl = 1:length(SaarlandSavingsOptimum(:,1))
    % optimum value
    SaarlandSavings(SaveSaarl,1) = SaarlandSavingsOptimum(SaveSaarl,:);
    % result of algorithm
    SaarlandSavings(SaveSaarl,2) = SaarlandSavingsShortestPathPlatoon(SaveSaarl,:) + (SaarlandAllSavingsShortestPath(SaveSaarl,:) - SaarlandSavingsShortestPath(SaveSaarl,:));
    % difference between optimum and algorithm
    SaarlandSavings(SaveSaarl,3) = SaarlandSavings(SaveSaarl,2) - SaarlandSavings(SaveSaarl,1);
    % difference in percent
    SaarlandSavings(SaveSaarl,4) = 100*(SaarlandSavings(SaveSaarl,2) - SaarlandSavings(SaveSaarl,1)) / SaarlandSavings(SaveSaarl,2);
    
end


% names for output
SaarlandSavings = array2table(SaarlandSavings);
SaarlandSavings.Properties.RowNames = {'10';'30';'50';'70'};
SaarlandSavings.Properties.VariableNames = {'OptimumValue' 'AlgorithmResult' 'DifferenceToOptimum' 'DifferenceInPercent'};

% output
SaarlandSavings
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%ENDE SAARLAND %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%% Thüringen
edges = 9819;
rows = T.Edges == edges ;


% change table to array to make the sums
ThueringenPerformanceAllTimes = table2array(T(rows, varsAllTimes));
ThueringenPerformanceWithoutLP = table2array(T(rows, varsWithoutLP));
ThueringenPerformanceOnlyGrouping = table2array(T(rows, varsOnlyGrouping));
ThueringenPerformanceOnlyLP = table2array(T(rows, varsOnlyLP));
ThueringenPerformanceLPtime = table2array(T(rows, varsLPtime));


% fill matrix with values
ThueringenTimes = zeros(length(ThueringenPerformanceAllTimes(:,1)),5);
for PerfThuer = 1:length(ThueringenPerformanceAllTimes(:,1))
    ThueringenTimes(PerfThuer,1) = sum(ThueringenPerformanceAllTimes(PerfThuer,:));
    ThueringenTimes(PerfThuer,2) = sum(ThueringenPerformanceWithoutLP(PerfThuer,:));
    ThueringenTimes(PerfThuer,3) = sum(ThueringenPerformanceOnlyGrouping(PerfThuer,:));
    ThueringenTimes(PerfThuer,4) = sum(ThueringenPerformanceOnlyLP(PerfThuer,:));
    ThueringenTimes(PerfThuer,5) = ThueringenPerformanceLPtime(PerfThuer,:);
end

% names for output
ThueringenTimes = array2table(ThueringenTimes);
ThueringenTimes.Properties.RowNames = {'10';'30';'50';'70';'71';'72'};
ThueringenTimes.Properties.VariableNames = {'allTimes' 'withoutLP' 'OnlyGrouping' 'OnlyLP' 'LPTime'};

% output
ThueringenTimes
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%% Savings Test %%%%%%%%%%%%

% change table to array to make the sums
ThueringenSavingsOptimum = table2array(T(rows,varsRealOptimum));
ThueringenAllSavingsShortestPath = table2array(T(rows,varsAllShortestPath));
ThueringenSavingsShortestPath = table2array(T(rows,varsShortestPath));
ThueringenSavingsShortestPathPlatoon = table2array(T(rows,varsShortestPathPlatoon));

% fill matrix with values
ThueringenSavings = zeros(length(ThueringenSavingsOptimum(:,1)),4);
for SaveThuer = 1:length(ThueringenSavingsOptimum(:,1))
    % optimum value
    ThueringenSavings(SaveThuer,1) = ThueringenSavingsOptimum(SaveThuer,:);
    % result of algorithm
    ThueringenSavings(SaveThuer,2) = ThueringenSavingsShortestPathPlatoon(SaveThuer,:) + (ThueringenAllSavingsShortestPath(SaveThuer,:) - ThueringenSavingsShortestPath(SaveThuer,:));
    % difference between optimum and algorithm
    ThueringenSavings(SaveThuer,3) = ThueringenSavings(SaveThuer,2) - ThueringenSavings(SaveThuer,1);
    % difference in percent
    ThueringenSavings(SaveThuer,4) = 100*(ThueringenSavings(SaveThuer,2) - ThueringenSavings(SaveThuer,1)) / ThueringenSavings(SaveThuer,2);
    
end


% names for output
ThueringenSavings = array2table(ThueringenSavings);
ThueringenSavings.Properties.RowNames = {'10';'30';'50';'70';'71';'72'};
ThueringenSavings.Properties.VariableNames = {'OptimumValue' 'AlgorithmResult' 'DifferenceToOptimum' 'DifferenceInPercent'};

% output
ThueringenSavings











%%%%%%%%%%%%%%%%%%%%%%%%%%%




%%%%%%%%% Nds
edges = 41074;
rows = T.Edges == edges ;


% change table to array to make the sums
NdsPerformanceAllTimes = table2array(T(rows, varsAllTimes));
NdsPerformanceWithoutLP = table2array(T(rows, varsWithoutLP));
NdsPerformanceOnlyGrouping = table2array(T(rows, varsOnlyGrouping));
NdsPerformanceOnlyLP = table2array(T(rows, varsOnlyLP));
NdsPerformanceLPtime = table2array(T(rows, varsLPtime));


% fill matrix with values
NdsTimes = zeros(length(NdsPerformanceAllTimes(:,1)),5);
for PerfNds = 1:length(NdsPerformanceAllTimes(:,1))
    NdsTimes(PerfNds,1) = sum(NdsPerformanceAllTimes(PerfNds,:));
    NdsTimes(PerfNds,2) = sum(NdsPerformanceWithoutLP(PerfNds,:));
    NdsTimes(PerfNds,3) = sum(NdsPerformanceOnlyGrouping(PerfNds,:));
    NdsTimes(PerfNds,4) = sum(NdsPerformanceOnlyLP(PerfNds,:));
    NdsTimes(PerfNds,5) = NdsPerformanceLPtime(PerfNds,:);
end

% names for output
NdsTimes = array2table(NdsTimes);
NdsTimes.Properties.RowNames = {'10';'30';'50';'70'};
NdsTimes.Properties.VariableNames = {'allTimes' 'withoutLP' 'OnlyGrouping' 'OnlyLP' 'LPTime'};

% output
NdsTimes
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%% Savings Test %%%%%%%%%%%%
% the real optimum calculated by LP for whole Problem
varsRealOptimum = {'Optimum'};
% the sum of the shortestPath of all vehicles
varsAllShortestPath = {'VShortestPath'};
% the sum of the shortest path of the assigned vehicles
varsShortestPath = {'SumSP'};
%the platooned distance of the assigned vehicles
varsShortestPathPlatoon = {'SumPSP'};



% change table to array to make the sums
NdsSavingsOptimum = table2array(T(rows,varsRealOptimum));
NdsAllSavingsShortestPath = table2array(T(rows,varsAllShortestPath));
NdsSavingsShortestPath = table2array(T(rows,varsShortestPath));
NdsSavingsShortestPathPlatoon = table2array(T(rows,varsShortestPathPlatoon));

% fill matrix with values
NdsSavings = zeros(length(NdsSavingsOptimum(:,1)),4);
for SaveNds = 1:length(NdsSavingsOptimum(:,1))
    % optimum value
    NdsSavings(SaveNds,1) = NdsSavingsOptimum(SaveNds,:);
    % result of algorithm
    NdsSavings(SaveNds,2) = NdsSavingsShortestPathPlatoon(SaveNds,:) + (NdsAllSavingsShortestPath(SaveNds,:) - NdsSavingsShortestPath(SaveNds,:));
    % difference between optimum and algorithm
    NdsSavings(SaveNds,3) = NdsSavings(SaveNds,2) - NdsSavings(SaveNds,1);
    % difference in percent
    NdsSavings(SaveNds,4) = 100*(NdsSavings(SaveNds,2) - NdsSavings(SaveNds,1)) / NdsSavings(SaveNds,2);
    
end


% names for output
NdsSavings = array2table(NdsSavings);
NdsSavings.Properties.RowNames = {'10';'30';'50';'70'};
NdsSavings.Properties.VariableNames = {'OptimumValue' 'AlgorithmResult' 'DifferenceToOptimum' 'DifferenceInPercent'};

% output
NdsSavings

%%%%%%%%%%%%%%%%%%%%%%%%%%%




%%%%%%%%% NRW
edges = 41074;
rows = T.Edges == edges ;

%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%












%%%%%%%%%%%%%%%%%%%%%%% Savings to Opt %%%%%%%%%%%%%%%%%%%%%%%




%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%




end