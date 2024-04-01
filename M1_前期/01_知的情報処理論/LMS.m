%{
function [e w] = lms(d, u, L = 128, mu = 1.0)
  % d：観測信号
  % u：参照信号
  % L：フィルタ長
  len = length(u);
  w = zeros(L, 1);
  e(1:L-1) = zeros(L-1, 1);

  for t = L: len
    e(t) = d(t) - w' * u(t-L+1:t, 1);
    w = w + 2 * mu * e(t) * u(t-L+1:t, 1);
  endfor
  w = flipud(w);
end
%}

%インパルス応答のよみ取り
[audio_data,sample_rate] = audioread('L0e000a.wav');
disp(audio_data);


%インパルス応答の情報　1行の状態
len_sample = length(audio_data);
% num_channels = size(audio_data,2);

%ガウス雑音の情報を読み込み配列に格納　参照信号u_t
%u_t = dlmread("gaussian-noise.txt");
u = randn(len_sample, 1);

%インパルス応答とガウス雑音の畳み込みを計算し結果を配列に格納　観測信号d_t
#sameで指定することで畳み込みの結果がu_tと同じ長さになる　デフォルトでは16383+16383-1=32765となり不適
d = conv(audio_data, u,'same');





mu = 0.00001;
w_old = zeros(1, num_samples).';
w_new = zeros(1, num_samples).';
tic();
for t = 1:num_samples
  w_new = w_old + ( 2 * mu * (d(t) - w_old.' * u) * u);
  w_old = w_new;
end
elapsed_time = toc ();
disp(w_old);



final_error = d_t - w_old.' * u_t;
disp('final_error');
disp(final_error);


size_final_error = norm(final_error,2);
disp('size of final_error');
disp(size_final_error);
disp('elapsed_time');
disp(elapsed_time);
