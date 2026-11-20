      subroutine rel_sec(dr)
      real*8 dr
      character*22 dstre, dstrs
      integer*4 mm, dd, yy
      character*8 zeit
      integer*4 values(8)

      external dsds2ds

      dstrs='01.01.1980 00:00:00.00'
      dstre='01.01.1980 00:00:00.00'
      call date_and_time(values=values)
      mm=values(2)
      dd=values(3)
      yy=mod(values(1),100)
      write(zeit,'(i2.2,":",i2.2,":",i2.2)')
     &          values(5), values(6), values(7)
      dstre(12:13)=zeit(1:2)
      dstre(15:16)=zeit(4:5)
      dstre(18:19)=zeit(7:8)
      write(dstre(1:2), '(i2)') dd
      write(dstre(4:5), '(i2)') mm
      write(dstre(9:10),'(i2)') yy


      call dsds2ds(dstre, dstrs, dr)


      return
      end
