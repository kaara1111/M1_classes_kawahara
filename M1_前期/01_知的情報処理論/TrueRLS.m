%インパルス応答のよみ取り
[audio_data,sample_rate] = audioread('AKG-K240-L.wav');

%インパルス応答の長さ
len_sample = length(audio_data);

%ガウス雑音を作成　参照信号u
u = randn(len_sample, 1);

%インパルス応答とガウス雑音の畳み込みを計算し結果を配列に格納　観測信号d
d = conv(audio_data, u,'same');

function [E, W, time] = RLS(u, d, M=64, lambda=0.9, epsilon=0.0001)
  len_sample = length(u);
  W = zeros(1,M).';
  P = epsilon * eye(M);
  %P_new = zeros(M);
  E(1:M-1) = zeros(M-1,1);%誤差を格納する配列　M個までは0で初期化
  tic();
  for t = M:len_sample
    g = (lambda^-1 / (1 + (lambda^-1 * d(t-M+1:t).' * P * d(t-M+1:t)))) * P * d(t-M+1:t);
    E(t) = d(t) - W.' * d(t-M+1:t);
    W = W + E(t) * g;
    P = lambda^-1 * (eye(M) - g * d(t-M+1:t).')* P;
  end
  execution_time = toc ();
endfunction

M=128;%フィルタの長さ
epsilon = 0.0001;
lambda = 0.9;
%{
W_old = zeros(1,M).';
W_new = zeros(1,M).';
P_old = epsilon * eye(M);
P_new = zeros(M);
E(1:M-1) = zeros(M-1,1);%誤差を格納する配列　M個までは0で初期化
tic();
for t = M:len_sample
  g = (lambda^-1 / (1 + (lambda^-1 * d(t-M+1:t).' * P_old * d(t-M+1:t)))) * P_old * d(t-M+1:t);
  E(t) = audio_data(t) - W_old.' * d(t-M+1:t);
  W_new = W_old + E(t) * g;
  W_old = W_new;
  P_new = lambda^-1 * (eye(M) - g * d(t-M+1:t).')* P_old;
  P_old = P_new;
end
execution_time = toc ();
%}
[E, W, time] = RLS(u, d, M, lambda, epsilon)

disp('execution time');
disp(execution_time);

log_values = 10 * log10(E);

x = 1:length(E);
plot(x, log_values);
xlabel('time (sample)');
ylabel('power of error');
title('plot of error');

figure(2)
legend('RLS(ε=0.0001,M=500)');

