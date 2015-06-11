import Data.Maybe
import Data.List
probs = [0.3, 0.15, 0.25, 0.1, 0.2]
orig = [0, 2, 4, 1]

cprobs xs = reverse $ foldl (\acc x -> (x + head acc): acc) [0] xs
cp = cprobs probs

encodeh [] cp u l = (u, l)
encodeh (x:xs) cp l u = let r = u - l
                            xx = fromInteger x
                            uu = cp !! (xx + 1)
                            ll = cp !! xx
                         in encodeh xs cp (l + r * ll) (l + r * uu)

encode xs cp = encodeh xs cp 0 1

-- with infinite precision, decode will get infinite sequence
decodeh v cp ret
  | length ret >= 10 = reverse ret
  | otherwise = let idx = (fromJust $ findIndex (> v) cp) - 1
                    l = cp !! idx
                    u = cp !! (idx + 1)
                    r = u - l
                    vv = (v - l) / r
                 in decodeh vv cp (idx:ret)

decode v cp = decodeh v cp []
